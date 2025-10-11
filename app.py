import streamlit as st
import pandas as pd
import json
import random
import time
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List
import PyPDF2
import matplotlib.pyplot as plt

# ---------------------------
# Constants & Data Dir
# ---------------------------
APP_TITLE = "CrackIt — Interview Prep"
DATA_DIR = Path("user_data")
DATA_DIR.mkdir(exist_ok=True)
COMM_FILE = Path("community.json")
if not COMM_FILE.exists():
    COMM_FILE.write_text(json.dumps({"posts": []}, indent=2))

# Example question bank (expandable)
QUESTION_BANK = {
    "Data Structures": [
        {"q": "What is a stack? Provide use-cases.", "a": "LIFO DS; use for recursion, backtracking, undo functionality."},
        {"q": "Array vs Linked List differences.", "a": "Arrays: contiguous memory, O(1) access. LinkedList: dynamic, O(n) access."}
    ],
    "Algorithms": [
        {"q": "Explain binary search and complexity.", "a": "On sorted arrays, divide-and-conquer. Complexity O(log n)."},
        {"q": "What is dynamic programming?", "a": "Optimization technique using memoization/tabulation for overlapping subproblems."}
    ],
    "DBMS": [
        {"q": "What is normalization?", "a": "Process to remove redundancy using normal forms (1NF, 2NF, 3NF...)."}
    ],
    "Operating Systems": [
        {"q": "What is deadlock? How to prevent it?", "a": "Processes wait forever for resources. Prevent by ordering, avoiding hold-and-wait."}
    ],
    "HR": [
        {"q": "Tell me about yourself (structure)", "a": "Present-Past-Future: current role, background, what you seek next."},
        {"q": "Strengths & Weaknesses - how to answer", "a": "Be specific, provide examples; for weakness, show improvement steps."}
    ]
}

# ---------------------------
# Helpers: persistence & user data
# ---------------------------
def user_file(username: str) -> Path:
    safe = "".join(c for c in username if c.isalnum() or c in (" ", "_", "-")).strip() or "Guest"
    return DATA_DIR / f"{safe}.json"

def load_user(username: str) -> Dict:
    f = user_file(username)
    if f.exists():
        try:
            return json.loads(f.read_text())
        except:
            return {}
    return {}

def save_user(username: str, payload: Dict):
    f = user_file(username)
    f.write_text(json.dumps(payload, indent=2))

def load_community() -> Dict:
    return json.loads(COMM_FILE.read_text())

def save_community(payload: Dict):
    COMM_FILE.write_text(json.dumps(payload, indent=2))

# ---------------------------
# UI Styles (professional palette)
# ---------------------------
PAGE_STYLE = """
<style>
/* page background gradient */
[data-testid="stAppViewContainer"] {
background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 50%, #eef2ff 100%);
background-attachment: fixed;
font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
}
/* card */
.card {
background: white;
border-radius: 14px;
padding: 18px;
box-shadow: 0 6px 22px rgba(16,24,40,0.08);
transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.card:hover { transform: translateY(-6px); box-shadow: 0 14px 40px rgba(16,24,40,0.12); }
/* header */
.app-header {
padding: 14px 18px;
border-radius: 12px;
background: linear-gradient(90deg,#6366f1,#8b5cf6);
color: white;
box-shadow: 0 6px 20px rgba(59,53,102,0.14);
}
/* small muted */
.small-muted { color: #6b7280; font-size: 0.95rem; }
</style>
"""

st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")
st.markdown(PAGE_STYLE, unsafe_allow_html=True)

# ---------------------------
# Small utilities
# ---------------------------
def format_date(d):
    if isinstance(d, (str,)):
        return d
    if isinstance(d, (datetime, date)):
        return d.isoformat()
    return str(d)

def increment_progress(username: str, area: str, amount=1):
    ud = load_user(username)
    ud.setdefault("progress", {})
    ud["progress"][area] = ud["progress"].get(area, 0) + amount
    # timeline for tracker
    ud.setdefault("timeline", {})
    today = date.today().isoformat()
    ud["timeline"][today] = ud["timeline"].get(today, 0) + amount
    save_user(username, ud)

# ---------------------------
# Pages Implementation
# ---------------------------

def onboarding_page(username: str):
    st.markdown('<div class="app-header"><h2 style="margin:6px 0 0 0">👋 Welcome to CrackIt</h2><div class="small-muted">Your personalized interview coach</div></div>', unsafe_allow_html=True)
    st.markdown("")
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Tell us a bit about you")
        name = st.text_input("Full name", value=username)
        role = st.selectbox("Primary goal", ["Software Engineer", "Data Scientist", "Frontend Engineer", "Backend Engineer", "Other"])
        experience = st.selectbox("Experience level", ["Student / Fresher", "1-2 years", "3-5 years", "5+ years"])
        skills = st.text_input("Key skills (comma-separated)", placeholder="Python, Data Structures, SQL")
        if st.button("Save profile"):
            ud = load_user(name)
            ud["profile"] = {"name": name, "role": role, "experience": experience, "skills": skills}
            ud.setdefault("created", datetime.now().isoformat())
            save_user(name, ud)
            st.success("Profile saved — welcome, " + name + "!")
            st.session_state["username"] = name
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Quick Start")
        st.write("- Go to **Daily Challenges** and try today's task")
        st.write("- Use **Mock Interview** to get real practice")
        st.write("- Upload your resume in **Resume Review**")
        st.markdown("</div>", unsafe_allow_html=True)

def dashboard_page(username: str, user_data: Dict):
    st.markdown('<div class="card"><h3>📊 Dashboard</h3><p class="small-muted">Overview of your practice</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    completed = sum(user_data.get("progress", {}).values()) if user_data.get("progress") else 0
    mocks = user_data.get("mock_count", 0)
    notes_chars = len(user_data.get("notes", "")) if "notes" in user_data else 0
    streak = user_data.get("streak", 0)
    cols[0].metric("Practice Points", completed)
    cols[1].metric("Mocks Taken", mocks)
    cols[2].metric("Notes Length", f"{notes_chars} chars")
    cols[3].metric("Streak (days)", streak)
    st.markdown("</div>", unsafe_allow_html=True)

    # Recent activity
    st.markdown("<div class='card' style='margin-top:12px'>", unsafe_allow_html=True)
    st.subheader("Recent Activity")
    timeline = user_data.get("timeline", {})
    if timeline:
        df = pd.DataFrame(list(timeline.items()), columns=["date", "points"]).sort_values("date")
        st.table(df.tail(7).set_index("date"))
    else:
        st.write("No activity yet — start your first challenge!")
    st.markdown("</div>", unsafe_allow_html=True)

def mock_interview_page(username: str, user_data: Dict):
    st.markdown("<div class='card'><h3>🎤 Mock Interview</h3><p class='small-muted'>Practice with randomized questions — write answers and compare with model answers</p></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col2:
        num_q = st.selectbox("Number of questions", [3,5,7,10], index=1)
        include_hr = st.checkbox("Include HR questions", True)
        style = st.selectbox("Style", ["Mixed", "Technical only", "HR only"], index=0)
        if st.button("Start Mock"):
            # build pool
            pool = []
            for t, qlist in QUESTION_BANK.items():
                if style == "Technical only" and t == "HR": continue
                if style == "HR only" and t != "HR": continue
                pool.extend([{"topic": t, "q": q["q"], "a": q["a"]} for q in qlist])
            if not pool:
                st.warning("No questions available for chosen filter.")
            else:
                selected = random.sample(pool, min(num_q, len(pool)))
                st.session_state["mock"] = {"questions": selected, "idx": 0, "score": 0, "answers": []}

    if "mock" in st.session_state:
        mock = st.session_state["mock"]
        idx = mock["idx"]
        qs = mock["questions"]
        if idx < len(qs):
            item = qs[idx]
            st.markdown(f"**Q{idx+1} ({item['topic']}):** {item['q']}")
            ans = st.text_area("Your answer:", key=f"mock_ans_{idx}", height=140)
            cola, colb = st.columns([1,2])
            with cola:
                if st.button("Show Model Answer", key=f"show_{idx}"):
                    st.info(item["a"])
            with colb:
                if st.button("Next", key=f"next_{idx}"):
                    # rudimentary match
                    user_words = set((ans or "").lower().split())
                    model_words = set(item["a"].lower().split())
                    overlap = len(user_words & model_words)
                    if overlap >= 2:
                        mock["score"] += 1
                    mock["answers"].append({"q": item["q"], "user": ans, "model": item["a"], "topic": item["topic"]})
                    mock["idx"] += 1
                    save_user(username, user_data)  # persist rudimentary state
                    st.rerun()
        else:
            total = len(qs)
            score = mock["score"]
            st.success(f"Finished — Score {score}/{total}")
            st.write("Review:")
            for a in mock["answers"]:
                st.markdown(f"- **Q:** {a['q']}")
                st.write(f"  - Your answer: {a['user'] or '_No answer_'}")
                st.write(f"  - Model answer: {a['model']}")
            # update user progress & mock count
            user_data["mock_count"] = user_data.get("mock_count", 0) + 1
            increment_progress(username, "practice_points", amount=score)
            save_user(username, user_data)
            del st.session_state["mock"]

def question_bank_page(username: str, user_data: Dict):
    st.markdown('<div class="card"><h3>📚 Question Bank</h3><p class="small-muted">Browse, search, and favorite questions</p></div>', unsafe_allow_html=True)
    topic = st.selectbox("Filter by topic", ["All"] + list(QUESTION_BANK.keys()))
    query = st.text_input("Search text (enter keywords):")
    show_fav = st.checkbox("Show only favorites", False)
    # build results
    results = []
    for t, qlist in QUESTION_BANK.items():
        if topic != "All" and t != topic:
            continue
        for q in qlist:
            results.append({"topic": t, "q": q["q"], "a": q["a"]})
    if query:
        results = [r for r in results if query.lower() in (r["q"] + r["a"]).lower()]
    # favorites in user_data
    favs = set(user_data.get("favorites", []))
    for i, r in enumerate(results):
        key = f"qb_{i}"
        with st.expander(f"{r['topic']} — {r['q']}"):
            st.write(r["a"])
            cols = st.columns([1,1,2])
            if cols[0].button("Mark Done", key=f"done_{i}"):
                increment_progress(username, r["topic"], amount=1)
                st.success("Marked — progress updated.")
                user_data = load_user(username)
            if cols[1].button(("Unfavorite" if r['q'] in favs else "Favorite"), key=f"fav_{i}"):
                user_data.setdefault("favorites", [])
                if r['q'] in user_data["favorites"]:
                    user_data["favorites"].remove(r['q'])
                else:
                    user_data["favorites"].append(r['q'])
                save_user(username, user_data)
                st.rerun()
            cols[2].write(f"Topic: {r['topic']}")

def resume_review_page(username: str, user_data: Dict):
    st.markdown('<div class="card"><h3>📄 Resume Review</h3><p class="small-muted">Upload PDF resume to extract text & get suggestions</p></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    if uploaded:
        try:
            reader = PyPDF2.PdfReader(uploaded)
            text = []
            for p in reader.pages:
                text.append(p.extract_text() or "")
            full = "\n".join(text).strip()
            st.success("Resume uploaded and text extracted.")
            st.text_area("Extracted text (preview):", value=full[:3000], height=240)
            # basic heuristics / suggestions
            suggestions = []
            if len(full) < 800:
                suggestions.append("Resume appears short — try to include more detail about projects & achievements.")
            if "experience" not in full.lower():
                suggestions.append("Consider adding an 'Experience' section with roles, dates, and accomplishments.")
            if "project" not in full.lower():
                suggestions.append("Add a 'Projects' section showcasing 2–4 concrete projects with outcomes.")
            if suggestions:
                st.markdown("### Suggestions")
                for s in suggestions:
                    st.write("- " + s)
            else:
                st.write("No obvious suggestions — great!")
            # store a resume timestamp in user profile
            user_data["resume_last_uploaded"] = datetime.now().isoformat()
            save_user(username, user_data)
        except Exception as e:
            st.error("Could not parse PDF. Try a different file. Error: " + str(e))

def daily_challenges_page(username: str, user_data: Dict):
    st.markdown('<div class="card"><h3>⚡ Daily Challenges</h3><p class="small-muted">Short daily tasks to build momentum</p></div>', unsafe_allow_html=True)
    # simple rotating challenge based on day
    day_index = date.today().day % 5
    challenges = [
        {"title": "Array Warmup", "desc": "Solve an easy arrays problem and explain your solution."},
        {"title": "System Design Snapshot", "desc": "Sketch a simple design for a URL shortener."},
        {"title": "Behavioral Prep", "desc": "Write a 60-second 'Tell me about yourself' pitch."},
        {"title": "DB Query", "desc": "Write an SQL query to find top 5 customers by spending."},
        {"title": "Optimization", "desc": "Take a naive algorithm and discuss how to optimize it."}
    ]
    c = challenges[day_index]
    st.markdown(f"### {c['title']}")
    st.write(c["desc"])
    if st.button("Mark challenge done"):
        increment_progress(username, "daily_challenges", amount=1)
        st.success("Nice — challenge recorded!")
        save_user(username, user_data)

def progress_tracker_page(username: str, user_data: Dict):
    st.markdown('<div class="card"><h3>📈 Progress Tracker</h3><p class="small-muted">Visual view of your practice over time</p></div>', unsafe_allow_html=True)
    timeline = user_data.get("timeline", {})
    if not timeline:
        st.info("No progress data yet — complete some activities to populate the chart.")
        return
    df = pd.DataFrame(list(timeline.items()), columns=["date", "points"]).sort_values("date")
    df['date'] = pd.to_datetime(df['date'])
    st.line_chart(df.set_index('date')['points'].cumsum())
    # small matplotlib chart for custom styling
    fig, ax = plt.subplots(figsize=(6,2.5))
    ax.plot(df['date'], df['points'].cumsum(), marker='o', linewidth=2)
    ax.set_title("Cumulative Practice Points")
    ax.set_ylabel("Points")
    ax.grid(alpha=0.2)
    st.pyplot(fig)

def community_page(username: str, user_data: Dict):
    st.markdown('<div class="card"><h3>💬 Community</h3><p class="small-muted">Share tips and see others'+"'"+' posts</p></div>', unsafe_allow_html=True)
    comm = load_community()
    name = st.text_input("Your display name", value=username)
    msg = st.text_area("Write something to share", height=90)
    if st.button("Post"):
        if not msg.strip():
            st.warning("Write something meaningful before posting.")
        else:
            comm.setdefault("posts", [])
            comm["posts"].insert(0, {"name": name, "msg": msg, "time": datetime.now().isoformat()})
            save_community(comm)
            st.success("Posted to community!")
            st.rerun()
    st.markdown("### Recent posts")
    for p in comm.get("posts", [])[:50]:
        st.markdown(f"**{p['name']}** • {p['time']}")
        st.write(p['msg'])
        st.markdown("---")

def settings_page(username: str, user_data: Dict):
    st.markdown('<div class="card"><h3>⚙️ Settings</h3><p class="small-muted">Manage preferences & data</p></div>', unsafe_allow_html=True)
    theme = st.selectbox("Theme preference (affects visuals)", ["Professional (default)", "High-Contrast", "Soft Pastel"])
    if st.button("Save Preferences"):
        user_data["prefs"] = {"theme": theme}
        save_user(username, user_data)
        st.success("Preferences saved.")
    if st.button("Reset my progress"):
        confirm = st.checkbox("I confirm I want to reset my progress (this will not delete profile)", key="confirm_reset")
        if confirm:
            user_data.pop("timeline", None)
            user_data.pop("progress", None)
            user_data.pop("mock_count", None)
            save_user(username, user_data)
            st.success("Progress reset.")
    st.markdown("Data is stored locally in the `user_data/` folder.")

# ---------------------------
# App Shell
# ---------------------------
def main():
    st.sidebar.title(APP_TITLE)
    st.sidebar.caption("Professional interview prep — built with Streamlit")

    # user selection
    username = st.sidebar.text_input("Profile name", value=st.session_state.get("username", "Guest"))
    if st.sidebar.button("Load profile"):
        st.session_state["username"] = username
        st.rerun()
    st.session_state["username"] = st.session_state.get("username", username)

    # load user data
    username = st.session_state["username"]
    user_data = load_user(username)

    # Navigation
    menu = ["Onboarding","Dashboard","Mock Interview","Question Bank","Resume Review","Daily Challenges","Progress Tracker","Community","Setting"]
    choice = st.sidebar.radio("Navigate", menu)

    # header row
    st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center'><div><h1 style='margin:0'>{APP_TITLE}</h1><div class='small-muted'>Prepare with confidence — consistent practice wins</div></div><div style='text-align:right'><small class='small-muted'>Signed in: {username}</small></div></div>", unsafe_allow_html=True)
    st.markdown("---")

    # route pages
    if choice == "Onboarding":
        onboarding_page(username)
    elif choice == "Dashboard":
        dashboard_page(username, user_data)
    elif choice == "Mock Interview":
        mock_interview_page(username, user_data)
    elif choice == "Question Bank":
        question_bank_page(username, user_data)
    elif choice == "Resume Review":
        resume_review_page(username, user_data)
    elif choice == "Daily Challenges":
        daily_challenges_page(username, user_data)
    elif choice == "Progress Tracker":
        progress_tracker_page(username, user_data)
    elif choice == "Community":
        community_page(username, user_data)
    elif choice == "Setting":
        settings_page(username, user_data)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("Built with ❤️ • Tip: Your data is saved on the server where you run this app (folder `user_data`).", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

