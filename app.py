import streamlit as st
import cv2
import numpy as np
import face_recognition
from PIL import Image
import pandas as pd
from datetime import date

from encodings_manager import (
    load_encodings, add_face, delete_face, get_registered_names
)
from attendance_manager import (
    mark_attendance, get_attendance, get_today_attendance, init_db
)

# --------------------------- Config ---------------------------
st.set_page_config(
    page_title="Face Attendance System",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

TOLERANCE = 0.45  # Lower = stricter

# --------------------------- Helpers ---------------------------
def process_image(image: Image.Image):
    """Convert PIL → RGB numpy array"""
    img = np.array(image.convert("RGB"))
    return img


def detect_and_encode(rgb_image):
    boxes = face_recognition.face_locations(rgb_image, model="hog")
    encodings = face_recognition.face_encodings(rgb_image, boxes)
    return boxes, encodings


def recognize(rgb_image):
    known_encodings, known_names = load_encodings()
    if not known_encodings:
        return [], [], "No registered faces found."

    boxes, encodings = detect_and_encode(rgb_image)
    results = []

    for encoding in encodings:
        distances = face_recognition.face_distance(known_encodings, encoding)
        matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=TOLERANCE)

        name = "Unknown"
        confidence = 0.0
        if len(distances) > 0:
            best_idx = np.argmin(distances)
            if matches[best_idx]:
                name = known_names[best_idx]
                confidence = (1 - distances[best_idx]) * 100

        results.append({"name": name, "confidence": confidence})

    return boxes, results, None


def draw_boxes(rgb_image, boxes, results):
    img = rgb_image.copy()
    for (top, right, bottom, left), res in zip(boxes, results):
        name = res["name"]
        conf = res["confidence"]
        color = (0, 200, 0) if name != "Unknown" else (0, 0, 220)
        label = f"{name} ({conf:.1f}%)" if name != "Unknown" else "Unknown"

        cv2.rectangle(img, (left, top), (right, bottom), color, 2)
        cv2.rectangle(img, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(img, label, (left + 6, bottom - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    return img


# --------------------------- Sidebar ---------------------------
st.sidebar.title("👤 Face Attendance")
menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📝 Register Face", "✅ Mark Attendance", "📊 Attendance Records", "⚙️ Manage Faces"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"📅 Today: **{date.today().strftime('%d %b %Y')}**")
registered = get_registered_names()
st.sidebar.metric("Registered Faces", len(registered))

# --------------------------- Pages ---------------------------
if menu == "🏠 Home":
    st.title("Face Recognition Attendance System")
    st.markdown("""
    ### Welcome!
    A professional, contactless attendance system powered by AI face recognition.

    **Features**
    - 📸 Easy face registration
    - ✅ One-click attendance marking
    - 🛡️ Duplicate prevention (same day)
    - 📊 Daily & historical reports
    - 📥 CSV export
    - 🧹 Face management
    """)
    st.success("Select a module from the sidebar to get started.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Registered People", len(registered))
    with col2:
        today_df = get_today_attendance()
        st.metric("Present Today", len(today_df))
    with col3:
        st.metric("System Status", "Online ✅")


elif menu == "📝 Register Face":
    st.header("📝 Register New Face")
    st.markdown("Capture a clear frontal face photo and enter the person's name.")

    name = st.text_input("Full Name", placeholder="e.g. John Doe")
    picture = st.camera_input("Capture Face", key="reg_cam")

    if st.button("Register Face", type="primary", use_container_width=True):
        if not name.strip():
            st.error("Please enter a name.")
        elif picture is None:
            st.error("Please capture a photo.")
        else:
            rgb = process_image(Image.open(picture))
            boxes, encodings = detect_and_encode(rgb)

            if len(encodings) == 0:
                st.error("No face detected. Please try again with better lighting.")
            elif len(encodings) > 1:
                st.warning("Multiple faces detected. Please capture only one face.")
            else:
                add_face(encodings[0], name)
                st.success(f"✅ **{name}** registered successfully!")
                st.balloons()


elif menu == "✅ Mark Attendance":
    st.header("✅ Mark Attendance")
    st.markdown("Take a photo. Recognized faces will be marked **Present** automatically.")

    picture = st.camera_input("Capture for Attendance", key="att_cam")

    if picture:
        rgb = process_image(Image.open(picture))
        boxes, results, error = recognize(rgb)

        if error:
            st.warning(error)
        elif not results:
            st.warning("No faces detected in the image.")
        else:
            annotated = draw_boxes(rgb, boxes, results)
            st.image(annotated, caption="Recognition Result", use_container_width=True)

            st.subheader("Recognition Results")
            for res in results:
                name = res["name"]
                conf = res["confidence"]

                if name == "Unknown":
                    st.error(f"❌ Unknown person (Confidence: {conf:.1f}%)")
                else:
                    success, msg = mark_attendance(name)
                    if success:
                        st.success(f"{msg} | Confidence: {conf:.1f}%")
                    else:
                        st.warning(msg)


elif menu == "📊 Attendance Records":
    st.header("📊 Attendance Records")

    tab1, tab2 = st.tabs(["Today", "All Records / Filter"])

    with tab1:
        df_today = get_today_attendance()
        if df_today.empty:
            st.info("No attendance recorded today.")
        else:
            st.dataframe(df_today, use_container_width=True, hide_index=True)
            st.download_button(
                "📥 Download Today's CSV",
                df_today.to_csv(index=False).encode("utf-8"),
                f"attendance_{date.today()}.csv",
                "text/csv"
            )

    with tab2:
        selected_date = st.date_input("Filter by Date", value=date.today())
        df = get_attendance(selected_date.isoformat())
        if df.empty:
            st.info("No records for this date.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "📥 Download CSV",
                df.to_csv(index=False).encode("utf-8"),
                f"attendance_{selected_date}.csv",
                "text/csv"
            )


elif menu == "⚙️ Manage Faces":
    st.header("⚙️ Manage Registered Faces")

    names = get_registered_names()
    if not names:
        st.info("No faces registered yet.")
    else:
        st.write(f"**{len(names)}** registered person(s):")
        for n in names:
            col1, col2 = st.columns([4, 1])
            col1.write(f"• {n}")
            if col2.button("🗑️ Delete", key=f"del_{n}"):
                deleted = delete_face(n)
                st.success(f"Deleted {deleted} encoding(s) for {n}")
                st.rerun()