import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="VoiceBridge-PST Dashboard",
    page_icon="🎙️",
    layout="wide"
)

# -------------------------------------------------------
# Rubric Dimensions
# -------------------------------------------------------

RUBRIC_COLUMNS = [
    "Conceptual_Clarity",
    "Pedagogical_Reasoning",
    "Learner_Centred_Explanation",
    "Misconception_Diagnosis",
    "Use_of_Example_Strategy",
    "Reflective_Thinking",
    "Voice_Written_Alignment"
]

RUBRIC_LABELS = {
    "Conceptual_Clarity": "Conceptual Clarity",
    "Pedagogical_Reasoning": "Pedagogical Reasoning",
    "Learner_Centred_Explanation": "Learner-Centred Explanation",
    "Misconception_Diagnosis": "Misconception Diagnosis",
    "Use_of_Example_Strategy": "Use of Example / Teaching Strategy",
    "Reflective_Thinking": "Reflective Thinking",
    "Voice_Written_Alignment": "Voice–Written Alignment"
}

MAX_SCORE_PER_TASK = len(RUBRIC_COLUMNS) * 5

# -------------------------------------------------------
# Required Columns
# -------------------------------------------------------

REQUIRED_COLUMNS = [
    "Student_ID",
    "Name",
    "Semester",
    "Pedagogy_Subject",
    "Task_ID",
    "Task_Category",
    "Prompt",
    "Voice_File_Name",
    "Written_Response",
    "Reflection_1",
    "Reflection_2",
    "Submission_Time"
]

# -------------------------------------------------------
# Subject-wise Prompt Bank: 10 Tasks per Subject
# -------------------------------------------------------

TASK_BANK = {
    "Pedagogy of Mathematics": [
        {"Task_ID": "MATH-01", "Task_Category": "Misconception Diagnosis", "Prompt": "A Class VI student says: “A larger denominator means a larger fraction.” How will you respond as a teacher?"},
        {"Task_ID": "MATH-02", "Task_Category": "Error Analysis", "Prompt": "A student solves 3x + 5 = 20 as 3x = 25. How will you identify and address this error?"},
        {"Task_ID": "MATH-03", "Task_Category": "Concept Explanation", "Prompt": "How would you introduce the concept of perimeter using examples from students’ daily life?"},
        {"Task_ID": "MATH-04", "Task_Category": "Concept Explanation", "Prompt": "How would you explain the difference between area and perimeter to Class VII students?"},
        {"Task_ID": "MATH-05", "Task_Category": "Assessment Decision", "Prompt": "After teaching equivalent fractions, how would you check whether students have understood the concept?"},
        {"Task_ID": "MATH-06", "Task_Category": "Inclusive Adaptation", "Prompt": "How would you adapt a geometry activity for a learner who has difficulty drawing diagrams?"},
        {"Task_ID": "MATH-07", "Task_Category": "Short Activity Design", "Prompt": "Suggest a short classroom activity to teach place value to middle-school students."},
        {"Task_ID": "MATH-08", "Task_Category": "Classroom Engagement", "Prompt": "Students are afraid of solving algebra questions on the board. What will you do?"},
        {"Task_ID": "MATH-09", "Task_Category": "Use of Example / Analogy", "Prompt": "How would you explain ratio using examples from daily life?"},
        {"Task_ID": "MATH-10", "Task_Category": "Error Analysis", "Prompt": "A student thinks 0.5 is smaller than 0.25 because 5 is smaller than 25. How will you respond?"}
    ],

    "Pedagogy of Science": [
        {"Task_ID": "SCI-01", "Task_Category": "Misconception Diagnosis", "Prompt": "A Class VII student says: “Heat and temperature are the same.” How will you respond as a teacher?"},
        {"Task_ID": "SCI-02", "Task_Category": "Concept Explanation", "Prompt": "How would you introduce the concept of evaporation using daily-life examples?"},
        {"Task_ID": "SCI-03", "Task_Category": "Short Activity Design", "Prompt": "Suggest a short classroom activity to show that air occupies space."},
        {"Task_ID": "SCI-04", "Task_Category": "Assessment Decision", "Prompt": "After teaching separation of substances, how would you check students’ understanding?"},
        {"Task_ID": "SCI-05", "Task_Category": "Misconception Diagnosis", "Prompt": "A student says: “Plants take their food directly from the soil.” How will you respond?"},
        {"Task_ID": "SCI-06", "Task_Category": "Inclusive Adaptation", "Prompt": "How would you adapt a science activity for a learner who is not confident in handling apparatus?"},
        {"Task_ID": "SCI-07", "Task_Category": "Classroom Engagement", "Prompt": "Students memorize scientific definitions but cannot relate them to experiments. What will you do?"},
        {"Task_ID": "SCI-08", "Task_Category": "Use of Example / Analogy", "Prompt": "How would you explain force using playground examples?"},
        {"Task_ID": "SCI-09", "Task_Category": "Concept Explanation", "Prompt": "How would you explain the difference between renewable and non-renewable resources?"},
        {"Task_ID": "SCI-10", "Task_Category": "Misconception Diagnosis", "Prompt": "A student says: “Heavier objects fall faster than lighter objects.” How will you respond?"}
    ],

    "Pedagogy of Social Science": [
        {"Task_ID": "SOC-01", "Task_Category": "Misconception Diagnosis", "Prompt": "A Class VIII student says: “Democracy only means voting.” How will you respond as a teacher?"},
        {"Task_ID": "SOC-02", "Task_Category": "Concept Explanation", "Prompt": "How would you introduce the concept of resources using local examples?"},
        {"Task_ID": "SOC-03", "Task_Category": "Classroom Engagement", "Prompt": "Students find history dates boring and disconnected from life. What will you do?"},
        {"Task_ID": "SOC-04", "Task_Category": "Assessment Decision", "Prompt": "After teaching fundamental rights, how would you check students’ understanding?"},
        {"Task_ID": "SOC-05", "Task_Category": "Inclusive Adaptation", "Prompt": "How would you adapt a map-reading activity for a learner who needs additional support?"},
        {"Task_ID": "SOC-06", "Task_Category": "Use of Example / Analogy", "Prompt": "How would you explain the concept of market using examples from a local shop or weekly market?"},
        {"Task_ID": "SOC-07", "Task_Category": "Error Analysis", "Prompt": "A student confuses weather with climate. How would you address this misunderstanding?"},
        {"Task_ID": "SOC-08", "Task_Category": "Short Activity Design", "Prompt": "Suggest a short activity to teach the idea of diversity in India."},
        {"Task_ID": "SOC-09", "Task_Category": "Concept Explanation", "Prompt": "How would you explain the difference between equality and equity to students?"},
        {"Task_ID": "SOC-10", "Task_Category": "Assessment Decision", "Prompt": "How would you assess whether students can connect a social science concept with current society?"}
    ],

    "Pedagogy of English": [
        {"Task_ID": "ENG-01", "Task_Category": "Misconception Diagnosis", "Prompt": "A student can read a passage aloud but cannot infer meaning. How will you support the learner?"},
        {"Task_ID": "ENG-02", "Task_Category": "Concept Explanation", "Prompt": "How would you introduce descriptive writing using classroom objects?"},
        {"Task_ID": "ENG-03", "Task_Category": "Classroom Engagement", "Prompt": "Students hesitate to speak in English during class. What will you do?"},
        {"Task_ID": "ENG-04", "Task_Category": "Assessment Decision", "Prompt": "After teaching a poem, how would you check comprehension beyond memorization?"},
        {"Task_ID": "ENG-05", "Task_Category": "Inclusive Adaptation", "Prompt": "How would you support a learner who understands ideas but struggles to write in English?"},
        {"Task_ID": "ENG-06", "Task_Category": "Use of Example / Analogy", "Prompt": "How would you explain the difference between literal and implied meaning using simple examples?"},
        {"Task_ID": "ENG-07", "Task_Category": "Error Analysis", "Prompt": "A student writes grammatically correct sentences but cannot organize a paragraph. How will you respond?"},
        {"Task_ID": "ENG-08", "Task_Category": "Short Activity Design", "Prompt": "Suggest a short activity to improve students’ vocabulary through context."},
        {"Task_ID": "ENG-09", "Task_Category": "Concept Explanation", "Prompt": "How would you teach the idea of character analysis in a short story?"},
        {"Task_ID": "ENG-10", "Task_Category": "Assessment Decision", "Prompt": "How would you assess students’ speaking ability without making them anxious?"}
    ],

    "Pedagogy of Hindi": [
        {"Task_ID": "HIN-01", "Task_Category": "Misconception Diagnosis", "Prompt": "A student memorizes a कविता but cannot explain its भावार्थ. How will you respond?"},
        {"Task_ID": "HIN-02", "Task_Category": "Concept Explanation", "Prompt": "How would you introduce मुहावरे using daily-life situations?"},
        {"Task_ID": "HIN-03", "Task_Category": "Classroom Engagement", "Prompt": "Students are not interested in पाठ-वाचन. What will you do?"},
        {"Task_ID": "HIN-04", "Task_Category": "Assessment Decision", "Prompt": "After teaching a कहानी, how would you check whether students understood the central idea?"},
        {"Task_ID": "HIN-05", "Task_Category": "Inclusive Adaptation", "Prompt": "How would you support a learner who has difficulty expressing ideas in written Hindi?"},
        {"Task_ID": "HIN-06", "Task_Category": "Use of Example / Analogy", "Prompt": "How would you explain अलंकार using examples from familiar poems or songs?"},
        {"Task_ID": "HIN-07", "Task_Category": "Error Analysis", "Prompt": "A student writes answers by memorizing lines but does not explain in their own words. How will you address this?"},
        {"Task_ID": "HIN-08", "Task_Category": "Short Activity Design", "Prompt": "Suggest a short activity to teach पर्यायवाची शब्द effectively."},
        {"Task_ID": "HIN-09", "Task_Category": "Concept Explanation", "Prompt": "How would you teach पत्र लेखन in a meaningful classroom way?"},
        {"Task_ID": "HIN-10", "Task_Category": "Assessment Decision", "Prompt": "How would you assess students’ understanding of a poem beyond recitation?"}
    ],

    "Pedagogy of Commerce": [
        {"Task_ID": "COM-01", "Task_Category": "Concept Explanation", "Prompt": "How would you explain the difference between profit and revenue using a simple classroom example?"},
        {"Task_ID": "COM-02", "Task_Category": "Misconception Diagnosis", "Prompt": "A student says: “Sales and profit are the same.” How will you respond?"},
        {"Task_ID": "COM-03", "Task_Category": "Use of Example / Analogy", "Prompt": "How would you explain assets and liabilities using examples from daily life?"},
        {"Task_ID": "COM-04", "Task_Category": "Assessment Decision", "Prompt": "After teaching journal entries, how would you check whether students can apply debit and credit rules?"},
        {"Task_ID": "COM-05", "Task_Category": "Error Analysis", "Prompt": "A student records a cash purchase on the wrong side of an account. How will you diagnose and address the error?"},
        {"Task_ID": "COM-06", "Task_Category": "Classroom Engagement", "Prompt": "Students find accounting rules mechanical and boring. What teaching strategy will you use?"},
        {"Task_ID": "COM-07", "Task_Category": "Short Activity Design", "Prompt": "Suggest a short classroom activity to teach demand and supply."},
        {"Task_ID": "COM-08", "Task_Category": "Inclusive Adaptation", "Prompt": "How would you support a learner who struggles with numerical examples in commerce?"},
        {"Task_ID": "COM-09", "Task_Category": "Concept Explanation", "Prompt": "How would you introduce the concept of banking services using local examples?"},
        {"Task_ID": "COM-10", "Task_Category": "Assessment Decision", "Prompt": "How would you assess whether students can connect business concepts with real market situations?"}
    ],

    "Pedagogy of Computer Science": [
        {"Task_ID": "CS-01", "Task_Category": "Concept Explanation", "Prompt": "How would you explain the difference between hardware and software using classroom examples?"},
        {"Task_ID": "CS-02", "Task_Category": "Misconception Diagnosis", "Prompt": "A student says: “The internet and the web are the same.” How will you respond?"},
        {"Task_ID": "CS-03", "Task_Category": "Use of Example / Analogy", "Prompt": "How would you explain the concept of an algorithm using a daily-life example?"},
        {"Task_ID": "CS-04", "Task_Category": "Error Analysis", "Prompt": "A student writes code without understanding the logic behind it. How will you address this?"},
        {"Task_ID": "CS-05", "Task_Category": "Assessment Decision", "Prompt": "After teaching loops, how would you check whether students understand repetition in programming?"},
        {"Task_ID": "CS-06", "Task_Category": "Short Activity Design", "Prompt": "Suggest a short unplugged activity to teach binary numbers."},
        {"Task_ID": "CS-07", "Task_Category": "Classroom Engagement", "Prompt": "Some students are afraid of coding and avoid participation. What will you do?"},
        {"Task_ID": "CS-08", "Task_Category": "Inclusive Adaptation", "Prompt": "How would you support a learner who has limited access to a computer outside class?"},
        {"Task_ID": "CS-09", "Task_Category": "Concept Explanation", "Prompt": "How would you explain data privacy to school students using simple examples?"},
        {"Task_ID": "CS-10", "Task_Category": "Assessment Decision", "Prompt": "How would you assess whether students can apply computational thinking to a non-computer problem?"}
    ]
}

PEDAGOGY_SUBJECTS = list(TASK_BANK.keys())

# -------------------------------------------------------
# Helper Functions
# -------------------------------------------------------

def initialize_session():
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame(
            columns=REQUIRED_COLUMNS + RUBRIC_COLUMNS + ["Total_Score", "Percentage", "Feedback"]
        )

    if "audio_files" not in st.session_state:
        st.session_state.audio_files = {}

    if "page" not in st.session_state:
        st.session_state.page = "Home"


def calculate_scores(df):
    df = df.copy()

    for col in RUBRIC_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    df["Total_Score"] = df[RUBRIC_COLUMNS].sum(axis=1, skipna=True)
    df["Percentage"] = (df["Total_Score"] / MAX_SCORE_PER_TASK) * 100

    return df


def convert_df_to_excel(df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="VoiceBridge_PST_Data")

    return output.getvalue()


def generate_feedback(row):
    available_scores = {}

    for col in RUBRIC_COLUMNS:
        if col in row.index and pd.notna(row[col]):
            available_scores[col] = row[col]

    if not available_scores:
        return "Rubric scores are not available for this response."

    strongest = max(available_scores, key=available_scores.get)
    weakest = min(available_scores, key=available_scores.get)

    feedback_map = {
        "Conceptual_Clarity": "Strengthen clarity of the core concept or pedagogical issue.",
        "Pedagogical_Reasoning": "Give stronger justification for the selected teaching response.",
        "Learner_Centred_Explanation": "Connect the explanation more clearly with learners’ needs and classroom context.",
        "Misconception_Diagnosis": "Identify the exact misconception or learning difficulty more precisely.",
        "Use_of_Example_Strategy": "Use more concrete examples, activities, analogies, or classroom strategies.",
        "Reflective_Thinking": "Add deeper reflection on strengths, limitations, and possible improvement.",
        "Voice_Written_Alignment": "Ensure that the written response clearly follows the oral reasoning."
    }

    return (
        f"Strongest area: {RUBRIC_LABELS[strongest]}. "
        f"Needs improvement: {RUBRIC_LABELS[weakest]}. "
        f"Suggested action: {feedback_map[weakest]}"
    )


def sort_task_ids(task_id):
    try:
        return int(str(task_id).split("-")[-1])
    except:
        return str(task_id)


def set_page(page_name):
    st.session_state.page = page_name


initialize_session()

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

st.sidebar.title("🎙️ VoiceBridge-PST")
st.sidebar.caption("Activity and Analytics Platform")

st.sidebar.markdown("### For Participants")
if st.sidebar.button("Activity Submission", use_container_width=True):
    set_page("Activity Submission")

st.sidebar.markdown("### For Teacher Educator")
if st.sidebar.button("Home", use_container_width=True):
    set_page("Home")
if st.sidebar.button("Review Responses", use_container_width=True):
    set_page("Review Responses")
if st.sidebar.button("Score Responses", use_container_width=True):
    set_page("Score Responses")
if st.sidebar.button("Diagnostic Profile", use_container_width=True):
    set_page("Diagnostic Profile")
if st.sidebar.button("Task Analytics", use_container_width=True):
    set_page("Task Analytics")
if st.sidebar.button("Download Data", use_container_width=True):
    set_page("Download Data")

st.sidebar.divider()

current_df = calculate_scores(st.session_state.data)

if len(current_df) > 0:
    st.sidebar.metric("Participants", current_df["Student_ID"].nunique())
    st.sidebar.metric("Submissions", len(current_df))
else:
    st.sidebar.info("No submissions yet.")

page = st.session_state.page

# -------------------------------------------------------
# Page 1: Home
# -------------------------------------------------------

if page == "Home":
    st.markdown("# 🎙️ VoiceBridge-PST Dashboard")
    st.markdown("### Voice-First Micro-Pedagogical Reasoning Activity and Analytics Platform")

    st.markdown(
        """
        <div style="margin-top: 6px; line-height: 1.25;">
            <span style="font-size: 14px; color: #666;">Conceptualized and Developed by</span><br>
            <b>Dr. Meenakshi Dwivedi</b><br>
            Assistant Professor<br>
            Department of Education / School of Education<br>
            Mahatma Jyotiba Phule Rohilkhand University, Bareilly, Uttar Pradesh, India
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("## Purpose")

    st.markdown("""
    The **VoiceBridge-PST Dashboard** is a web-based activity and analytics platform designed for 
    voice-first micro-pedagogical reasoning assessment among pre-service teachers.

    It enables pre-service teachers to respond to subject-specific pedagogical prompts through:

    - voice reasoning,
    - short written pedagogical response,
    - reflective response.

    It also enables the teacher educator or researcher to:

    - review submissions,
    - score responses using a rubric,
    - examine voice–written alignment,
    - generate diagnostic profiles,
    - analyse task-wise performance,
    - download scored data.
    """)

    st.markdown("---")

    st.markdown("## Dashboard Workflow")
    st.markdown("**Activity Submission → Review Responses → Score Responses → Diagnostic Profile → Task Analytics → Download Data**")

    st.markdown("---")

    st.markdown("## Pedagogy Subjects Included")
    for subject in PEDAGOGY_SUBJECTS:
        st.markdown(f"- {subject}")

    st.markdown("---")

    st.markdown("## Assessment Dimensions")
    st.markdown("""
    1. Conceptual Clarity  
    2. Pedagogical Reasoning  
    3. Learner-Centred Explanation  
    4. Misconception Diagnosis  
    5. Use of Example / Teaching Strategy  
    6. Reflective Thinking  
    7. Voice–Written Alignment  
    """)

    st.info(
        "The current version is suitable for testing and demonstration. "
        "For broad institutional use, connect the app with Google Sheets, Firebase, Supabase, or another database."
    )

# -------------------------------------------------------
# Page 2: Activity Submission
# -------------------------------------------------------

elif page == "Activity Submission":
    st.title("Pre-service Teacher Activity Submission")

    st.markdown("""
    Select your pedagogy subject and task. Then upload your voice response, write a short pedagogical response, 
    and submit your reflections.
    """)

    st.divider()

    st.markdown("## Select Subject and Task")

    subject_col, category_col = st.columns(2)

    with subject_col:
        selected_subject = st.selectbox("Pedagogy Subject", PEDAGOGY_SUBJECTS)

    available_categories = sorted(
        list(set(task["Task_Category"] for task in TASK_BANK[selected_subject]))
    )

    with category_col:
        selected_category = st.selectbox("Task Category", available_categories)

    filtered_tasks = [
        task for task in TASK_BANK[selected_subject]
        if task["Task_Category"] == selected_category
    ]

    task_options = {
        f'{task["Task_ID"]} — {task["Prompt"][:75]}...': task
        for task in filtered_tasks
    }

    selected_task_label = st.selectbox("Select Prompt", list(task_options.keys()))
    selected_task = task_options[selected_task_label]

    task_id = selected_task["Task_ID"]
    task_category = selected_task["Task_Category"]
    prompt = selected_task["Prompt"]

    st.markdown("### Pedagogical Prompt")
    st.info(prompt)

    st.divider()

    with st.form("activity_submission_form", clear_on_submit=True):
        st.markdown("## Participant Details")

        col1, col2 = st.columns(2)

        with col1:
            student_id = st.text_input("Student ID / Participant Code", placeholder="Example: PST01")
            name = st.text_input("Name", placeholder="Optional")

        with col2:
            semester = st.selectbox(
                "Semester",
                [
                    "B.Ed. Semester I",
                    "B.Ed. Semester II",
                    "B.Ed. Semester III",
                    "B.Ed. Semester IV"
                ]
            )

            st.text_input("Selected Pedagogy Subject", value=selected_subject, disabled=True)

        st.markdown("## Voice Reasoning")
        st.caption("Record your oral explanation on your phone/laptop and upload the audio file. Suggested duration: 2–3 minutes.")

        audio_file = st.file_uploader(
            "Upload Audio Response",
            type=["mp3", "wav", "m4a", "ogg"]
        )

        st.markdown("## Written Pedagogical Response")
        written_response = st.text_area(
            "Write a short response of about 150–200 words.",
            height=180
        )

        st.markdown("## Reflection")
        reflection_1 = st.text_area(
            "Reflection 1: What pedagogical issue, learner difficulty, error, or misconception did you identify?",
            height=100
        )

        reflection_2 = st.text_area(
            "Reflection 2: What example, activity, explanation, or teaching strategy would you use?",
            height=100
        )

        submitted = st.form_submit_button("Submit Response", type="primary")

    if submitted:
        if not student_id.strip():
            st.error("Please enter Student ID / Participant Code.")
        elif audio_file is None:
            st.error("Please upload an audio response.")
        elif not written_response.strip():
            st.error("Please write the pedagogical response.")
        else:
            audio_key = f"{student_id}_{task_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{audio_file.name}"
            st.session_state.audio_files[audio_key] = audio_file.getvalue()

            new_row = {
                "Student_ID": student_id.strip(),
                "Name": name.strip(),
                "Semester": semester,
                "Pedagogy_Subject": selected_subject,
                "Task_ID": task_id,
                "Task_Category": task_category,
                "Prompt": prompt,
                "Voice_File_Name": audio_key,
                "Written_Response": written_response.strip(),
                "Reflection_1": reflection_1.strip(),
                "Reflection_2": reflection_2.strip(),
                "Submission_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Feedback": ""
            }

            for col in RUBRIC_COLUMNS:
                new_row[col] = np.nan

            new_df = pd.DataFrame([new_row])
            st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)
            st.session_state.data = calculate_scores(st.session_state.data)

            st.success("Your response has been submitted successfully.")
            st.balloons()

# -------------------------------------------------------
# Page 3: Review Responses
# -------------------------------------------------------

elif page == "Review Responses":
    st.title("Review Responses")

    df = calculate_scores(st.session_state.data)

    if len(df) == 0:
        st.warning("No responses available yet.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            student_ids = sorted(df["Student_ID"].dropna().unique())
            selected_student = st.selectbox("Select Student ID", student_ids)

        student_df = df[df["Student_ID"] == selected_student].copy()

        with col2:
            task_ids = sorted(student_df["Task_ID"].dropna().unique(), key=sort_task_ids)
            selected_task = st.selectbox("Select Task", task_ids)

        row = student_df[student_df["Task_ID"] == selected_task].iloc[0]

        st.divider()

        st.subheader(f"{selected_student} | {selected_task}")

        info_col1, info_col2, info_col3 = st.columns(3)
        info_col1.metric("Subject", row["Pedagogy_Subject"])
        info_col2.metric("Category", row["Task_Category"])
        info_col3.metric("Current Score", f"{row['Total_Score']:.0f}/{MAX_SCORE_PER_TASK}")

        st.markdown("### Prompt")
        st.info(row["Prompt"])

        st.markdown("### Audio Response")

        audio_name = row["Voice_File_Name"]

        if audio_name in st.session_state.audio_files:
            st.audio(st.session_state.audio_files[audio_name])
        else:
            st.caption("Audio file is not available in this session. For broad use, connect cloud storage.")

        st.markdown("### Written Pedagogical Response")
        st.write(row["Written_Response"])

        st.markdown("### Reflections")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Diagnostic Reflection**")
            st.write(row["Reflection_1"] if pd.notna(row["Reflection_1"]) else "")

        with col_b:
            st.markdown("**Strategy Reflection**")
            st.write(row["Reflection_2"] if pd.notna(row["Reflection_2"]) else "")

        st.markdown("### Existing Scores")

        score_display = {
            RUBRIC_LABELS[col]: row[col] if pd.notna(row[col]) else "Not scored"
            for col in RUBRIC_COLUMNS
        }

        st.table(pd.DataFrame(score_display.items(), columns=["Dimension", "Score"]))

        if pd.notna(row.get("Feedback", "")) and str(row.get("Feedback", "")).strip():
            st.markdown("### Feedback")
            st.info(row["Feedback"])

# -------------------------------------------------------
# Page 4: Score Responses
# -------------------------------------------------------

elif page == "Score Responses":
    st.title("Score Responses")

    df = st.session_state.data.copy()

    if len(df) == 0:
        st.warning("No responses available yet.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            student_ids = sorted(df["Student_ID"].dropna().unique())
            selected_student = st.selectbox("Select Student ID", student_ids)

        student_df = df[df["Student_ID"] == selected_student].copy()

        with col2:
            task_ids = sorted(student_df["Task_ID"].dropna().unique(), key=sort_task_ids)
            selected_task = st.selectbox("Select Task", task_ids)

        idx = df[
            (df["Student_ID"] == selected_student) &
            (df["Task_ID"] == selected_task)
        ].index[0]

        row = df.loc[idx]

        st.divider()

        st.subheader(f"Scoring: {selected_student} | {selected_task}")

        st.markdown("### Prompt")
        st.info(row["Prompt"])

        with st.expander("View Response Material"):
            st.markdown("**Audio Response**")

            audio_name = row["Voice_File_Name"]

            if audio_name in st.session_state.audio_files:
                st.audio(st.session_state.audio_files[audio_name])
            else:
                st.caption("Audio file is not available in this session.")

            st.markdown("**Written Pedagogical Response**")
            st.write(row["Written_Response"])

            st.markdown("**Diagnostic Reflection**")
            st.write(row["Reflection_1"] if pd.notna(row["Reflection_1"]) else "")

            st.markdown("**Strategy Reflection**")
            st.write(row["Reflection_2"] if pd.notna(row["Reflection_2"]) else "")

        st.markdown("### Rubric Scores")

        scores = {}
        left_col, right_col = st.columns(2)

        for i, rubric_col in enumerate(RUBRIC_COLUMNS):
            current_value = row[rubric_col]

            if pd.isna(current_value):
                current_value = 3
            else:
                current_value = int(current_value)

            target_col = left_col if i % 2 == 0 else right_col

            with target_col:
                scores[rubric_col] = st.slider(
                    RUBRIC_LABELS[rubric_col],
                    min_value=1,
                    max_value=5,
                    value=current_value,
                    key=f"{selected_student}_{selected_task}_{rubric_col}"
                )

        total_score = sum(scores.values())
        percentage = (total_score / MAX_SCORE_PER_TASK) * 100

        col_a, col_b = st.columns(2)
        col_a.metric("Total Score", f"{total_score}/{MAX_SCORE_PER_TASK}")
        col_b.metric("Percentage", f"{percentage:.2f}%")

        feedback_text = st.text_area(
            "Teacher Educator Feedback",
            value=row["Feedback"] if "Feedback" in df.columns and pd.notna(row["Feedback"]) else "",
            height=120
        )

        if st.button("Generate Suggested Feedback"):
            temp_row = row.copy()
            for col, score in scores.items():
                temp_row[col] = score
            st.info(generate_feedback(temp_row))

        if st.button("Save Scores and Feedback", type="primary"):
            for rubric_col, score in scores.items():
                df.loc[idx, rubric_col] = score

            df.loc[idx, "Feedback"] = feedback_text.strip()

            df = calculate_scores(df)
            st.session_state.data = df

            st.success("Scores and feedback saved successfully.")

        st.caption("Scoring guide: 1 = Very weak | 2 = Weak | 3 = Moderate | 4 = Good | 5 = Excellent")

# -------------------------------------------------------
# Page 5: Diagnostic Profile
# -------------------------------------------------------

elif page == "Diagnostic Profile":
    st.title("Diagnostic Profile")

    df = calculate_scores(st.session_state.data)

    if len(df) == 0:
        st.warning("No responses available yet.")
    else:
        student_ids = sorted(df["Student_ID"].dropna().unique())
        selected_student = st.selectbox("Select Student ID", student_ids)

        student_df = df[df["Student_ID"] == selected_student].copy()
        student_df = student_df.sort_values("Task_ID", key=lambda x: x.map(sort_task_ids))

        st.divider()

        st.subheader(f"Diagnostic Profile: {selected_student}")

        name_value = student_df["Name"].iloc[0]
        semester_value = student_df["Semester"].iloc[0]
        subject_value = student_df["Pedagogy_Subject"].iloc[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Name", name_value if str(name_value).strip() else "Not provided")
        col2.metric("Semester", semester_value)
        col3.metric("Subject", subject_value)

        total_score = student_df["Total_Score"].sum()
        max_possible = len(student_df) * MAX_SCORE_PER_TASK
        overall_percentage = (total_score / max_possible) * 100 if max_possible else 0

        col4, col5, col6 = st.columns(3)
        col4.metric("Total Score", f"{total_score:.0f}/{max_possible}")
        col5.metric("Overall %", f"{overall_percentage:.2f}%")
        col6.metric("Tasks Submitted", len(student_df))

        rubric_means = student_df[RUBRIC_COLUMNS].mean(numeric_only=True)

        if rubric_means.notna().sum() > 0:
            strongest = rubric_means.idxmax()
            weakest = rubric_means.idxmin()

            st.markdown(f"**Strongest Dimension:** {RUBRIC_LABELS[strongest]}")
            st.markdown(f"**Needs Improvement:** {RUBRIC_LABELS[weakest]}")

            st.markdown("### Dimension-wise Profile")

            fig, ax = plt.subplots(figsize=(10, 5))
            labels = [RUBRIC_LABELS[col] for col in RUBRIC_COLUMNS]
            values = [rubric_means[col] for col in RUBRIC_COLUMNS]

            ax.bar(labels, values)
            ax.set_ylabel("Average Score")
            ax.set_ylim(0, 5)
            ax.tick_params(axis="x", rotation=75)

            st.pyplot(fig)

            st.markdown("### Task-wise Progress")

            fig2, ax2 = plt.subplots(figsize=(8, 4))

            ax2.plot(student_df["Task_ID"], student_df["Total_Score"], marker="o")
            ax2.set_xlabel("Task")
            ax2.set_ylabel("Total Score")
            ax2.set_ylim(0, MAX_SCORE_PER_TASK)
            ax2.tick_params(axis="x", rotation=45)

            st.pyplot(fig2)

            st.markdown("### Diagnostic Note")

            latest_scored = student_df.dropna(subset=RUBRIC_COLUMNS, how="all")

            if not latest_scored.empty:
                latest_row = latest_scored.iloc[-1]
                st.info(generate_feedback(latest_row))
            else:
                st.info("No scored response available yet.")

        else:
            st.info("Rubric scores are not available yet.")

        st.markdown("### Submitted Task Data")
        st.dataframe(student_df, use_container_width=True)

# -------------------------------------------------------
# Page 6: Task Analytics
# -------------------------------------------------------

elif page == "Task Analytics":
    st.title("Task Analytics")

    df = calculate_scores(st.session_state.data)

    if len(df) == 0:
        st.warning("No responses available yet.")
    else:
        st.subheader("Dataset Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Participants", df["Student_ID"].nunique())
        col2.metric("Submissions", len(df))
        col3.metric("Pedagogy Subjects", df["Pedagogy_Subject"].nunique())
        col4.metric("Average Score", f"{df['Total_Score'].mean():.2f}")

        st.divider()

        st.markdown("### Task-wise Mean Score")

        task_summary = (
            df.groupby(["Task_ID", "Task_Category"])["Total_Score"]
            .agg(["mean", "std", "count"])
            .reset_index()
        )

        task_summary.rename(
            columns={
                "mean": "Mean Score",
                "std": "SD",
                "count": "Submissions"
            },
            inplace=True
        )

        task_summary["Task_Order"] = task_summary["Task_ID"].map(sort_task_ids)
        task_summary = task_summary.sort_values("Task_Order")

        st.dataframe(task_summary.drop(columns=["Task_Order"]), use_container_width=True)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(task_summary["Task_ID"], task_summary["Mean Score"])
        ax.set_xlabel("Task")
        ax.set_ylabel("Mean Total Score")
        ax.set_ylim(0, MAX_SCORE_PER_TASK)
        ax.tick_params(axis="x", rotation=45)
        st.pyplot(fig)

        st.markdown("### Dimension-wise Mean Scores")

        rubric_mean = df[RUBRIC_COLUMNS].mean(numeric_only=True)

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        labels = [RUBRIC_LABELS[col] for col in RUBRIC_COLUMNS]
        values = [rubric_mean[col] for col in RUBRIC_COLUMNS]

        ax2.bar(labels, values)
        ax2.set_ylabel("Average Score")
        ax2.set_ylim(0, 5)
        ax2.tick_params(axis="x", rotation=75)
        st.pyplot(fig2)

        st.markdown("### Subject-wise Summary")

        subject_summary = (
            df.groupby("Pedagogy_Subject")["Total_Score"]
            .agg(["mean", "std", "count"])
            .reset_index()
        )

        subject_summary.rename(
            columns={
                "mean": "Mean Score",
                "std": "SD",
                "count": "Submissions"
            },
            inplace=True
        )

        st.dataframe(subject_summary, use_container_width=True)

        st.markdown("### Category-wise Summary")

        category_summary = (
            df.groupby("Task_Category")["Total_Score"]
            .agg(["mean", "std", "count"])
            .reset_index()
        )

        category_summary.rename(
            columns={
                "mean": "Mean Score",
                "std": "SD",
                "count": "Submissions"
            },
            inplace=True
        )

        st.dataframe(category_summary, use_container_width=True)

        st.markdown("### Completion Status")

        completion = (
            df.groupby(["Student_ID", "Name", "Semester", "Pedagogy_Subject"])["Task_ID"]
            .count()
            .reset_index()
        )

        completion.rename(columns={"Task_ID": "Tasks_Submitted"}, inplace=True)

        st.dataframe(completion, use_container_width=True)

# -------------------------------------------------------
# Page 7: Download Data
# -------------------------------------------------------

elif page == "Download Data":
    st.title("Download Data")

    df = calculate_scores(st.session_state.data)

    if len(df) == 0:
        st.warning("No responses available yet.")
    else:
        st.markdown("Download the submitted and scored dataset for further analysis.")

        csv_data = df.to_csv(index=False).encode("utf-8")
        excel_data = convert_df_to_excel(df)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="VoiceBridge_PST_Data.csv",
                mime="text/csv"
            )

        with col2:
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name="VoiceBridge_PST_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.markdown("### Data Preview")
        st.dataframe(df, use_container_width=True)

        st.warning(
            "Important: In this testing version, uploaded audio files remain available only during the active Streamlit session. "
            "For real institutional use, connect the app with Google Drive, Firebase, Supabase, or another storage/database system."
        )
