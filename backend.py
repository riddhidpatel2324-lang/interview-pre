import json
import os

DB_FILE = "data.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}, "messages": []}, f)

def load_data():
    """Load all data from the database file."""
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Save all data to the database file."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_user(name, role):
    """Save or update user info."""
    data = load_data()
    data["users"][name] = {"role": role, "progress": 0}
    save_data(data)

def update_progress(name, progress):
    """Update user progress value."""
    data = load_data()
    if name in data["users"]:
        data["users"][name]["progress"] = progress
        save_data(data)

def add_message(user, msg):
    """Add a new community message."""
    data = load_data()
    data["messages"].append({"user": user, "msg": msg})
    save_data(data)

def get_messages():
    """Fetch all community messages."""
    data = load_data()
    return data["messages"]

def load_questions(category):
    """
    Load questions from JSON files based on category.
    Folder: /data
    Files: technical_questions.json, hr_behavioral_questions.json, case_study_questions.json
    """
    file_map = {
        "Technical": "data/technical_questions.json",
        "HR / Behavioral": "data/hr_behavioral_questions.json",
        "Case_Study / Product": "data/case_study_questions.json"
    }

    filename = file_map.get(category)
    if not filename:
        return []

    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Error reading {filename}: invalid JSON format.")
            return []
    else:
        print(f"⚠️ File not found: {filename}")
        return []


DB_FILE = "data.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}, "messages": []}, f)

def load_data():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_user(name, role):
    data = load_data()
    data["users"][name] = {"role": role, "progress": 0}
    save_data(data)

def update_progress(name, progress):
    data = load_data()
    if name in data["users"]:
        data["users"][name]["progress"] = progress
        save_data(data)

def add_message(user, msg):
    data = load_data()
    data["messages"].append({"user": user, "msg": msg})
    save_data(data)

def get_messages():
    data = load_data()
    return data["messages"]
