# 👤 Face Recognition Attendance System

**A modern, contactless, AI-powered attendance system** built with Streamlit, OpenCV, and the `face_recognition` library.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?logo=streamlit&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

<br>

> Register faces once → Mark attendance in seconds with a single photo → Get clean reports & CSV exports.

---

## ✨ Features

| Feature                    | Description                                              |
|---------------------------|----------------------------------------------------------|
| **Face Registration**     | Capture a clear photo and store 128-dimensional encoding |
| **One-Click Attendance**  | Recognize face → Automatically mark **Present**          |
| **Duplicate Prevention**  | One attendance record per person per day (SQLite unique constraint) |
| **Confidence Score**      | Shows matching confidence percentage                     |
| **Live Dashboard**        | Today’s attendance + historical records                  |
| **CSV Export**            | Download filtered attendance data instantly              |
| **Face Management**       | View and delete registered faces                         |
| **Fully Local**           | No cloud, no external API – all data stays on your machine |

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                     │
│   Home │ Register │ Mark Attendance │ Records │ Manage     │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                    Application Layer                       │
│  • Face Registration      • Recognition + Matching         │
│  • Attendance Marking     • Duplicate Check                │
│  • Reports & CSV Export   • Face Management                │
└──────────────┬──────────────────────────┬──────────────────┘
               │                          │
┌──────────────▼──────────┐  ┌────────────▼──────────────────┐
│   Face Encoding Store   │  │     Attendance Database       │
│   face_encodings.pkl    │  │   SQLite (attendance.db)      │
│   (name → 128-d vector) │  │   name + date + time + status │
└─────────────────────────┘  └───────────────────────────────┘
               │                          │
┌──────────────▼──────────────────────────▼──────────────────┐
│                 Computer Vision Layer                      │
│        OpenCV  +  face_recognition (dlib HOG encodings)    │
└────────────────────────────────────────────────────────────┘
--
## 📁 Project Structure

face-attendance-system/
├── app.py                      
├── encodings_manager.py        
├── attendance_manager.py      
├── README.md
└── data/                       
    ├── face_encodings.pkl      
    └── attendance.db           

--
## 🛠️ How to Use

1. Register a Face

Go to 📝 Register Face
Enter the person’s full name
Capture a clear, frontal face photo
Click Register Face
--
2. Mark Attendance

Go to ✅ Mark Attendance
Capture a photo of the person
The system recognizes the face and marks them Present with timestamp
If already marked today → shows a friendly warning
---
3. View & Export Records

Go to 📊 Attendance Records
View Today or filter by any date
Download CSV with one click
---
4. Manage Faces

Go to ⚙️ Manage Faces
See all registered people
Delete any face encoding when needed

---
