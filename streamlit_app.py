import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Initialize database connection
def init_db():
    conn = sqlite3.connect('growth_tracker.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            title TEXT,
            category TEXT,
            reflection TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS mistakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mistake TEXT,
            lesson TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

st.title("🌱 Focused Growth Tracker")
st.write("Track your milestones, reflect on lessons learned, and grow consistently.")

menu = ["Dashboard", "Log Milestone", "Log Mistake", "View History"]
choice = st.sidebar.selectbox("Navigation", menu)

conn = sqlite3.connect('growth_tracker.db')
c = conn.cursor()

if choice == "Dashboard":
    st.subheader("Performance Overview")
    
    milestones_df = pd.read_sql("SELECT * FROM milestones", conn)
    mistakes_df = pd.read_sql("SELECT * FROM mistakes", conn)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Milestones Achieved", len(milestones_df))
    with col2:
        st.metric("Total Lessons Logged", len(mistakes_df))
        
    st.markdown("---")
    st.write("Keep pushing forward! Consistency is key to mastery.")

elif choice == "Log Milestone":
    st.subheader("Record a New Milestone")
    with st.form("milestone_form"):
        title = st.text_input("Milestone Title")
        category = st.selectbox("Category", ["Technical", "Academic", "Personal", "Other"])
        reflection = st.text_area("Key Takeaway / Reflection")
        submit = st.form_submit_button("Save Milestone")
        
        if submit and title:
            date_str = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO milestones (date, title, category, reflection) VALUES (?, ?, ?, ?)",
                      (date_str, title, category, reflection))
            conn.commit()
            st.success("Milestone saved successfully!")

elif choice == "Log Mistake":
    st.subheader("Log a Mistake & Lesson Learned")
    with st.form("mistake_form"):
        mistake_desc = st.text_area("What went wrong?")
        lesson_desc = st.text_area("What is the lesson learned?")
        submit = st.form_submit_button("Save Lesson")
        
        if submit and mistake_desc:
            date_str = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO mistakes (date, mistake, lesson) VALUES (?, ?, ?)",
                      (date_str, mistake_desc, lesson_desc))
            conn.commit()
            st.success("Lesson recorded! Every mistake is a step forward.")

elif choice == "View History":
    st.subheader("Growth History & Management")
    
    st.markdown("### Milestones")
    milestones_df = pd.read_sql("SELECT id, date, title, category, reflection FROM milestones", conn)
    st.dataframe(milestones_df, use_container_width=True)
    
    m_id_to_delete = st.number_input("Enter Milestone ID to permanently delete", min_value=0, step=1, key="del_m")
    if st.button("Delete Milestone"):
        c.execute("DELETE FROM milestones WHERE id = ?", (m_id_to_delete,))
        conn.commit()
        st.success(f"Milestone ID {m_id_to_delete} deleted!")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Mistakes & Learnings")
    mistakes_df = pd.read_sql("SELECT id, date, mistake, lesson FROM mistakes", conn)
    st.dataframe(mistakes_df, use_container_width=True)
    
    err_id_to_delete = st.number_input("Enter Mistake ID to permanently delete", min_value=0, step=1, key="del_err")
    if st.button("Delete Mistake"):
        c.execute("DELETE FROM mistakes WHERE id = ?", (err_id_to_delete,))
        conn.commit()
        st.success(f"Mistake ID {err_id_to_delete} deleted!")
        st.rerun()

conn.close()