import sqlite3
from datetime import datetime
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Focused Growth Tracker", page_icon="📈", layout="wide"
)

# Custom Styling for Cards and Reflections
st.markdown(
    """
    <style>
    .reflection-box {
        background-color: #FAFAF7 !important;
        border: 1px solid #E2D9CE !important;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Database Setup
def init_db():
  conn = sqlite3.connect("learning_tracker.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roadblock TEXT NOT NULL,
            lesson TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()


# Database Helpers
def get_milestones():
  conn = sqlite3.connect("learning_tracker.db")
  cursor = conn.cursor()
  cursor.execute("SELECT id, title, category, status FROM milestones")
  rows = cursor.fetchall()
  conn.close()
  return [
      {"id": r[0], "title": r[1], "category": r[2], "status": r[3]} for r in rows
  ]


def get_reflections():
  conn = sqlite3.connect("learning_tracker.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, roadblock, lesson, date FROM reflections ORDER BY id DESC"
  )
  rows = cursor.fetchall()
  conn.close()
  return [
      {"id": r[0], "roadblock": r[1], "lesson": r[2], "date": r[3]} for r in rows
  ]


# App Header
st.title("Focused Growth Tracker")
st.caption(
    "Embrace continuous learning, track your milestones, and turn roadblocks"
    " into lessons."
)

milestones = get_milestones()
reflections = get_reflections()

# Calculate Progress
total_count = len(milestones)
completed_count = sum(1 for m in milestones if m["status"] == "Completed")
percentage = (
    int((completed_count / total_count) * 100) if total_count > 0 else 0
)

# Overall Progress Section inside a clean card
with st.container(border=True):
  st.markdown("### Overall Progress")
  col_prog_info, col_prog_bar, col_prog_num = st.columns([2, 5, 1])
  with col_prog_info:
    st.write(f"**{completed_count} of {total_count}** milestones completed")
  with col_prog_bar:
    st.progress(percentage / 100)
  with col_prog_num:
    st.markdown(
        f"<h3 style='margin:0; color:#6A2C59;'>{percentage}%</h3>",
        unsafe_allow_html=True,
    )

st.write("")

# Main Layout Grid (2 Columns)
col1, col2 = st.columns(2, gap="large")

with col1:
  with st.container(border=True):
    st.subheader("Learning Milestones")
    st.caption("Add goals and track your technical learning journey.")

    # Add Milestone Form with Primary (Plum) Button
    with st.form("milestone_form", clear_on_submit=True):
      m_title = st.text_input(
          "Milestone Title", placeholder="e.g., Complete Python Flask module"
      )
      m_category = st.selectbox(
          "Category",
          ["Programming", "Algorithms", "Web Dev", "System Design"],
      )
      submitted_m = st.form_submit_button("Add Milestone", type="primary")

      if submitted_m and m_title:
        conn = sqlite3.connect("learning_tracker.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO milestones (title, category, status) VALUES (?, ?, ?)",
            (m_title, m_category, "Pending"),
        )
        conn.commit()
        conn.close()
        st.rerun()

    st.write("---")

    # Milestone List
    if milestones:
      for m in milestones:
        m_col1, m_col2 = st.columns([4, 1])
        with m_col1:
          status_icon = "✅" if m["status"] == "Completed" else "⏳"
          st.markdown(
              f"**{status_icon} {m['title']}** <br><span"
              f" style='font-size:11px; color:#786F66; background:#E2D9CE;"
              f" padding:2px 6px; border-radius:4px;'>{m['category']}</span>",
              unsafe_allow_html=True,
          )
        with m_col2:
          new_status = (
              "Pending" if m["status"] == "Completed" else "Completed"
          )
          btn_label = "Undo" if m["status"] == "Completed" else "Done"
          if st.button(btn_label, key=f"m_{m['id']}"):
            conn = sqlite3.connect("learning_tracker.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE milestones SET status = ? WHERE id = ?",
                (new_status, m["id"]),
            )
            conn.commit()
            conn.close()
            st.rerun()
        st.write("")
    else:
      st.info("No milestones added yet. Start tracking your goals!")

with col2:
  with st.container(border=True):
    st.subheader("Mistake-to-Lesson Journal")
    st.caption("Record roadblocks as feedback loops for growth.")

    # Add Reflection Form with Primary (Plum) Button
    with st.form("reflection_form", clear_on_submit=True):
      r_roadblock = st.text_input(
          "Roadblock", placeholder="What roadblock did you hit?"
      )
      r_lesson = st.text_area(
          "Lesson Learned", placeholder="What actionable lesson did you learn?"
      )
      submitted_r = st.form_submit_button("Log Reflection", type="primary")

      if submitted_r and r_roadblock and r_lesson:
        current_date = datetime.now().strftime("%b %d, %Y")
        conn = sqlite3.connect("learning_tracker.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reflections (roadblock, lesson, date) VALUES (?, ?, ?)",
            (r_roadblock, r_lesson, current_date),
        )
        conn.commit()
        conn.close()
        st.rerun()

    st.write("---")

    # Reflection List
    if reflections:
      for r in reflections:
        st.markdown(
            f"""
                <div class="reflection-box">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #786F66; margin-bottom: 4px;">
                        <span style="color: #9C3848; font-weight:600; text-transform:uppercase;">Roadblock</span>
                        <span>{r['date']}</span>
                    </div>
                    <div style="font-style: italic; font-weight: 500; margin-bottom: 8px;">"{r['roadblock']}"</div>
                    <div style="background-color: rgba(106, 44, 89, 0.06); padding: 8px 12px; border-radius: 6px; border-left: 3px solid #6A2C59; font-size: 14px;">
                        <strong>Lesson:</strong> {r['lesson']}
                    </div>
                </div>
                """,
            unsafe_allow_html=True,
        )
    else:
      st.info("No reflections logged yet. Turn your first challenge into a lesson!")