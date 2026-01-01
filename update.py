import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ==================== PAGE CONFIG & STUNNING THEME ====================
st.set_page_config(
    page_title="SMS Pro - School Management",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Beautiful Gradient Theme with Professional Styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom, #667eea, #764ba2);
        color: white;
    }
    h1, h2, h3 {
        color: white !important;
        text-align: center;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.4);
    }
    .stButton > button {
        border-radius: 12px;
        height: 3.8em;
        font-weight: bold;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .add-btn {background-color: #28a745 !important; color: white !important;}
    .add-btn:hover {background-color: #218838 !important; transform: translateY(-3px);}
    .update-btn {background-color: #007bff !important; color: white !important;}
    .update-btn:hover {background-color: #0056b3 !important; transform: translateY(-3px);}
    .delete-btn {background-color: #dc3545 !important; color: white !important;}
    .delete-btn:hover {background-color: #c82333 !important; transform: translateY(-3px);}
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        text-align: center;
        margin: 10px;
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50;
    }
    .stDataFrame {border-radius: 10px; overflow: hidden;}
</style>
""", unsafe_allow_html=True)

# Database Setup
conn = sqlite3.connect("school.db", check_same_thread=False)
c = conn.cursor()

# Create All Tables
c.execute('''CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT NOT NULL UNIQUE,
    class TEXT,
    section TEXT,
    age INTEGER,
    phone TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    teacher_id TEXT NOT NULL UNIQUE,
    subject TEXT,
    phone TEXT,
    email TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    amount REAL,
    payment_date TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_name TEXT,
    class TEXT,
    subject TEXT,
    max_marks INTEGER,
    date TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    isbn TEXT UNIQUE,
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER
)''')

c.execute('''CREATE TABLE IF NOT EXISTS timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class TEXT,
    day TEXT,
    period INTEGER,
    subject TEXT,
    teacher TEXT
)''')

conn.commit()

# ==================== SIDEBAR NAVIGATION ====================
st.sidebar.markdown("<h1 style='color:white; text-align:center;'>🏫 SMS Pro</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align:center; color:#bdc3c7;'>Advanced School Management</p>", unsafe_allow_html=True)

page = st.sidebar.radio("**Navigation**", [
    "🏠 Dashboard",
    "👨‍🎓 Students",
    "👩‍🏫 Teachers",
    "📅 Attendance",
    "💰 Fees Management",
    "📊 Exams",
    "📚 Library Books",
    "🗓️ Timetable"
], label_visibility="collapsed")

# ==================== UNIVERSAL CRUD FUNCTION ====================
def crud_module(icon_title, table, fields, display_cols):
    st.markdown(f"<h1>{icon_title}</h1>", unsafe_allow_html=True)
    
    tab_add, tab_manage = st.tabs(["➕ Add New Record", "📋 View & Manage"])

    with tab_add:
        with st.form("add_form", clear_on_submit=True):
            st.subheader("Add New Entry")
            inputs = {}
            cols = st.columns(2)
            for idx, (field, label) in enumerate(fields.items()):
                with cols[idx % 2]:
                    if "amount" in field or "copies" in field or "marks" in field or "period" in field or "age" in field:
                        inputs[field] = st.number_input(label, min_value=0 if "amount" in field else 1)
                    elif "date" in field:
                        inputs[field] = str(st.date_input(label, date.today()))
                    else:
                        inputs[field] = st.text_input(label)
            
            if st.form_submit_button("➕ Add Record", use_container_width=True):
                required = [k for k in fields if "*" in fields[k]]
                if all(inputs.get(k.replace("*","")) for k in required):
                    try:
                        cols_str = ", ".join(inputs.keys())
                        placeholders = ", ".join(["?"] * len(inputs))
                        c.execute(f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})", tuple(inputs.values()))
                        conn.commit()
                        st.success("✅ Record added successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Duplicate or invalid entry!")
                else:
                    st.warning("⚠️ Please fill required fields!")

    with tab_manage:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        if not df.empty:
            st.dataframe(df[display_cols], use_container_width=True)

            st.markdown("### ✏️ Update | 🗑️ Delete Record")
            record_id = st.number_input("Enter Record ID", min_value=1, step=1)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Load for Update", use_container_width=True):
                    if record_id in df["id"].values:
                        row = df[df["id"] == record_id].iloc[0]
                        for col in df.columns:
                            st.session_state[f"{table}_{col}"] = row[col]
                        st.session_state[f"{table}_edit_id"] = record_id
                        st.success("Record loaded for editing!")
                    else:
                        st.error("ID not found!")

            with col2:
                if st.button("🗑️ Delete Record", use_container_width=True):
                    if record_id in df["id"].values:
                        if st.checkbox("Confirm deletion"):
                            c.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
                            conn.commit()
                            st.success("Record deleted!")
                            st.rerun()

            # Update Form
            if f"{table}_edit_id" in st.session_state:
                st.markdown("### ✏️ Edit Record")
                with st.form("update_form"):
                    updated = {}
                    cols = st.columns(2)
                    for idx, (field, label) in enumerate(fields.items()):
                        default = st.session_state.get(f"{table}_{field}", "")
                        with cols[idx % 2]:
                            if "amount" in field or "copies" in field or "marks" in field or "period" in field or "age" in field:
                                updated[field] = st.number_input(label, value=int(default) if default else 0)
                            elif "date" in field:
                                updated[field] = str(st.date_input(label, value=date.fromisoformat(default) if default else date.today()))
                            else:
                                updated[field] = st.text_input(label, value=default)
                    
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        set_clause = ", ".join([f"{k}=?" for k in updated.keys()])
                        values = list(updated.values()) + [st.session_state[f"{table}_edit_id"]]
                        c.execute(f"UPDATE {table} SET {set_clause} WHERE id=?", values)
                        conn.commit()
                        st.success("Record updated successfully!")
                        # Clear session state
                        for key in list(st.session_state.keys()):
                            if key.startswith(table):
                                del st.session_state[key]
                        st.rerun()
        else:
            st.info("No records found. Add one using the 'Add New Record' tab!")

# ==================== DASHBOARD ====================
if page == "🏠 Dashboard":
    st.markdown("<h1>Welcome to SMS Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#ecf0f1;'>Advanced School Management System</h3>", unsafe_allow_html=True)

    cols = st.columns(7)
    modules = [
        ("👨‍🎓 Students", "students"),
        ("👩‍🏫 Teachers", "teachers"),
        ("📚 Books", "books"),
        ("📊 Exams", "exams"),
        ("💰 Fees Paid", "fees"),
        ("📅 Attendance Records", "attendance"),
        ("🗓️ Timetable Entries", "timetable")
    ]
    for col, (label, tbl) in zip(cols, modules):
        c.execute(f"SELECT COUNT(*) FROM {tbl}")
        count = c.fetchone()[0]
        with col:
            st.markdown(f"<div class='metric-card'><h2>{count}</h2><p style='color:#2c3e50; font-weight:bold;'>{label}</p></div>", unsafe_allow_html=True)

# ==================== MODULE ROUTING ====================
elif page == "👨‍🎓 Students":
    crud_module("👨‍🎓 Student Management", "students",
                {"name": "Full Name *", "roll_no": "Roll No *", "class": "Class", "section": "Section", "age": "Age", "phone": "Phone"},
                ["id", "name", "roll_no", "class", "section", "age", "phone"])

elif page == "👩‍🏫 Teachers":
    crud_module("👩‍🏫 Teacher Management", "teachers",
                {"name": "Full Name *", "teacher_id": "Teacher ID *", "subject": "Subject", "phone": "Phone", "email": "Email"},
                ["id", "name", "teacher_id", "subject", "phone", "email"])

elif page == "📅 Attendance":
    crud_module("📅 Attendance Records", "attendance",
                {"student_id": "Student ID *", "date": "Date", "status": "Status (Present/Absent/Late)"},
                ["id", "student_id", "date", "status"])

elif page == "💰 Fees Management":
    crud_module("💰 Fees Management", "fees",
                {"student_id": "Student ID *", "amount": "Amount Paid", "payment_date": "Payment Date", "status": "Status"},
                ["id", "student_id", "amount", "payment_date", "status"])

elif page == "📊 Exams":
    crud_module("📊 Exam Management", "exams",
                {"exam_name": "Exam Name *", "class": "Class", "subject": "Subject", "max_marks": "Max Marks", "date": "Exam Date"},
                ["id", "exam_name", "class", "subject", "max_marks", "date"])

elif page == "📚 Library Books":
    crud_module("📚 Library Management", "books",
                {"title": "Book Title *", "author": "Author", "isbn": "ISBN", "total_copies": "Total Copies"},
                ["id", "title", "author", "isbn", "total_copies", "available_copies"])

elif page == "🗓️ Timetable":
    crud_module("🗓️ Class Timetable", "timetable",
                {"class": "Class *", "day": "Day (Mon-Fri)", "period": "Period Number", "subject": "Subject", "teacher": "Teacher Name"},
                ["id", "class", "day", "period", "subject", "teacher"])

conn.close()
