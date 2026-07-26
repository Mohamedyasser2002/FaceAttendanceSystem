import os
import pickle
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ENCODINGS_PATH = DATA_DIR / "face_encodings.pkl"


def load_encodings():
    if not ENCODINGS_PATH.exists():
        return [], []
    with open(ENCODINGS_PATH, "rb") as f:
        data = pickle.load(f)
    return data.get("encodings", []), data.get("names", [])


def save_encodings(encodings, names):
    with open(ENCODINGS_PATH, "wb") as f:
        pickle.dump({"encodings": encodings, "names": names}, f)


def add_face(encoding, name):
    encodings, names = load_encodings()
    encodings.append(encoding)
    names.append(name.strip())
    save_encodings(encodings, names)


def delete_face(name):
    encodings, names = load_encodings()
    new_encodings, new_names = [], []
    for enc, n in zip(encodings, names):
        if n != name:
            new_encodings.append(enc)
            new_names.append(n)
    save_encodings(new_encodings, new_names)
    return len(names) - len(new_names)


def get_registered_names():
    _, names = load_encodings()
    return sorted(set(names))