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
# Constants
# -------------------------------------------------------

REQUIRED_COLUMNS = [
    "Student_ID",
    "Name",
    "Semester",
    "Pedagogy_Subject",
    "Task_No",
    "Prompt_Type",
    "Prompt",
    "Voice_File_Name",
    "Written_Response",
    "Reflection_1",
    "Reflection_2",
    "Submission_Time"
]

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

TASK_BANK = {
    "Task 1": {
        "Prompt_Type": "Misconception Diagnosis",
        "Prompt": "A Class VI student says: “A larger denominator means a larger fraction.” How will you respond as a teacher?"
    },
    "Task 2": {
        "Prompt_Type": "Classroom Response",
        "Prompt": "Some students are not participating in group work. What will you do as a teacher?"
    },
    "Task 3": {
        "Prompt_Type": "Inclusive Adaptation",
        "Prompt": "How would you adapt a classroom activity for a learner who needs additional learning support?"
    },
    "Task 4": {
        "Prompt_Type": "Assessment Decision",
        "Prompt": "After teaching a concept, how would you check whether students have understood it?"
    },
    "Task 5": {
        "Prompt_Type": "Pedagogical Explanation",
        "Prompt": "Explain how you would introduce a new concept using an example from students’ daily life."
    }
}


# -------------------------------------------------------
# Helper Functions
# -------------------------------------------------------

def initialize_session():
    if "responses" not in st.session_state:
        st.session_state.responses = pd.DataFrame(columns=REQUIRED_COLUMNS + RUBRIC_COLUMNS + ["Total_Score", "Percentage", "Feedback"])

    if "audio_files" not in st.session_state:
        st.session_state.audio_files = {}

    if "data" not in st.session_state:
        st.session_state.data = st.session_state.responses.copy()


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


def clean_task_order(task_value):
    try:
        return int(str(task_value).replace("Task", "").strip())
    except:
        return str(task_value)


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


def show_required_columns():
    st.code(
        """
Student_ID
Name
Semester
Pedagogy_Subject
Task_No
Prompt_Type
Prompt
Voice_File_Name
Written_Response
Reflection_1
Reflection_2
Submission_Time
        """,
        language="text"
    )


def create_sample_data():
    data = {
        "Student_ID": ["PST01", "PST01", "PST02"],
        "Name": ["Participant 1", "Participant 1", "Participant 2"],
        "Semester": ["B.Ed. Semester II", "B.Ed. Semester II", "B.Ed. Semester II"],
        "Pedagogy_Subject": ["Pedagogy of Mathematics", "Pedagogy of Mathematics", "Pedagogy of Science"],
        "Task_No": ["Task 1", "Task 2", "Task 1"],
        "Prompt_Type": ["Misconception Diagnosis", "Classroom Response", "Misconception Diagnosis"],
        "Prompt": [
            TASK_BANK["Task 1"]["Prompt"],
            TASK_BANK["Task 2"]["Prompt"],
            TASK_BANK["Task 1"]["Prompt"]
        ],
        "Voice_File_Name": ["sample_audio_1.mp3", "sample_audio_2.mp3", "sample_audio_3.mp3"],
        "Written_Response": [
            "I will first identify the misconception and use fraction strips to explain the idea.",
            "I will assign group roles and encourage participation through peer support.",
            "I will use concrete examples and ask the learner to compare fractions visually."
        ],
        "Reflection_1": [
            "The learner is confused between denominator size and fraction value.",
            "The issue may be lack of role clarity or confidence.",
            "The learner is comparing numbers without understanding part-whole relation."
        ],
        "Reflection_2": [
            "I will use paper folding or fraction circles.",
            "I will use group roles and guided participation.",
            "I will use diagrams and examples."
        ],
        "Submission_Time": [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
    }

    df = pd.DataFrame(data)

    for col in RUBRIC_COLUMNS:
        df[col] = np.nan

    df["Feedback"] = ""

    return calculate_scores(df)


initialize_session()

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

st.sidebar.title("🎙️ VoiceBridge-PST")
st.sidebar.caption("Activity and Analytics Platform")

page = st.sidebar.radio(
    "Menu",
    [
        "Home",
        "Activity Submission",
        "Upload Existing Data",
        "Review Responses",
        "Score Responses",
        "Diagnostic Profile",
        "Task Analytics",
        "Export Data"
    ]
)

st.sidebar.divider()

current_df = calculate_scores(st.session_state.data)

if len(current_df) > 0:
    st.sidebar.metric("Participants", current_df["Student_ID"].nunique())
    st.sidebar.metric("Submissions", len(current_df))
else:
    st.sidebar.info("No submissions yet.")


# -------------------------------------------------------
# Page 1: Home
# -------------------------------------------------------

if page == "Home":
    st.title("VoiceBridge-PST Dashboard")
    st.subheader("Voice-First Micro-Pedagogical Reasoning Activity and Analytics Platform")

    st.markdown("---")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### 🎙️")
        st.markdown("## VoiceBridge-PST")

    with col2:
        st.markdown("## Conceptualized and Developed by")
        st.markdown("**Dr. Meenakshi Dwivedi**")
        st.markdown("Assistant Professor")
        st.markdown("Department of Education / School of Education")
        st.markdown("Mahatma Jyotiba Phule Rohilkhand University, Bareilly, Uttar Pradesh, India")

    st.markdown("---")

    st.markdown("## Purpose")

    st.markdown("""
    The **VoiceBridge-PST Dashboard** is a web-based activity and analytics platform designed for 
    voice-first micro-pedagogical reasoning assessment among pre-service teachers.

    It enables pre-service teachers to respond to short pedagogical prompts through:

    - voice reasoning,
    - short written pedagogical response,
    - reflective response.

    It also enables the teacher educator or researcher to:

    - review submissions,
    - score responses using a rubric,
    - examine voice–written alignment,
    - generate diagnostic profiles,
    - analyse task-wise performance,
    - export scored data.
    """)

    st.markdown("---")

    st.markdown("## Dashboard Workflow")

    st.markdown("""
    **Activity Submission → Review Responses → Score Responses → Diagnostic Profile → Task Analytics → Export Data**
    """)

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
        "For broad use, this app should later be connected with Google Sheets, Firebase, Supabase, or another database. "
        "The present version is suitable for testing and demonstration."
    )


# -------------------------------------------------------
# Page 2: Activity Submission
# -------------------------------------------------------

elif page == "Activity Submission":
    st.title("Pre-service Teacher Activity Submission")

    st.markdown("""
    Complete the activity by reading the prompt, uploading your audio response, writing a short pedagogical response, 
    and submitting your reflections.
    """)

    st.divider()

    with st.form("activity_submission_form", clear_on_submit=True):
        st.markdown("### Participant Details")

        col1, col2 = st.columns(2)

        with col1:
            student_id = st.text_input("Student ID / Participant Code", placeholder="Example: PST01")
            name = st.text_input("Name", placeholder="Optional")

        with col2:
            semester = st.selectbox(
                "Semester",
                ["B.Ed. Semester I", "B.Ed. Semester II", "B.Ed. Semester III", "B.Ed. Semester IV", "Other"]
            )

            pedagogy_subject = st.selectbox(
                "Pedagogy Subject",
                [
                    "Pedagogy of Mathematics",
                    "Pedagogy of Science",
                    "Pedagogy of Social Science",
                    "Pedagogy of English",
                    "Pedagogy of Hindi",
                    "Pedagogy of Commerce",
                    "Pedagogy of Computer Science",
                    "Other"
                ]
            )

        st.markdown("### Select Task")

        task_no = st.selectbox("Task Number", list(TASK_BANK.keys()))
        prompt_type = TASK_BANK[task_no]["Prompt_Type"]
        prompt = TASK_BANK[task_no]["Prompt"]

        st.markdown("### Pedagogical Prompt")
        st.info(prompt)

        st.markdown("### Voice Reasoning")
        st.caption("Record your oral explanation on your phone/laptop and upload the audio file here. Suggested duration: 2–3 minutes.")

        audio_file = st.file_uploader(
            "Upload Audio Response",
            type=["mp3", "wav", "m4a", "ogg"]
        )

        st.markdown("### Written Pedagogical Response")
        written_response = st.text_area(
            "Write a short response of about 150–200 words.",
            height=180
        )

        st.markdown("### Reflection")
        reflection_1 = st.text_area(
            "Reflection 1: What pedagogical issue, learner difficulty, or misconception did you identify?",
            height=100
        )

        reflection_2 = st.text_area(
            "Reflection 2: What example, activity, or teaching strategy would you use?",
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
            audio_key = f"{student_id}_{task_no}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{audio_file.name}"
            st.session_state.audio_files[audio_key] = audio_file.getvalue()

            new_row = {
                "Student_ID": student_id.strip(),
                "Name": name.strip(),
                "Semester": semester,
                "Pedagogy_Subject": pedagogy_subject,
                "Task_No": task_no,
                "Prompt_Type": prompt_type,
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
# Page 3: Upload Existing Data
# -------------------------------------------------------

elif page == "Upload Existing Data":
    st.title("Upload Existing Data")

    st.markdown("""
    Use this page if responses were collected through Google Forms, Excel, or another external system.
    """)

    with st.expander("View required columns"):
        show_required_columns()

    uploaded_file = st.file_uploader(
        "Upload Excel or CSV file",
        type=["xlsx", "csv"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]

            if missing_cols:
                st.error("The uploaded file is missing required columns:")
                st.write(missing_cols)
            else:
                for col in RUBRIC_COLUMNS:
                    if col not in df.columns:
                        df[col] = np.nan

                if "Feedback" not in df.columns:
                    df["Feedback"] = ""

                df = calculate_scores(df)
                st.session_state.data = df

                st.success("Data uploaded successfully.")

                col1, col2, col3 = st.columns(3)
                col1.metric("Participants", df["Student_ID"].nunique())
                col2.metric("Submissions", len(df))
                col3.metric("Subjects", df["Pedagogy_Subject"].nunique())

                st.markdown("### Data Preview")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.divider()

    st.markdown("### Use Sample Data")

    if st.button("Load Sample Data"):
        df = create_sample_data()
        st.session_state.data = df

        st.success("Sample data loaded successfully.")
        st.dataframe(df, use_container_width=True)


# -------------------------------------------------------
# Page 4: Review Responses
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
            task_list = sorted(
                student_df["Task_No"].dropna().unique(),
                key=clean_task_order
            )
            selected_task = st.selectbox("Select Task", task_list)

        row = student_df[student_df["Task_No"] == selected_task].iloc[0]

        st.divider()

        st.subheader(f"{selected_student} | {selected_task}")

        info_col1, info_col2, info_col3 = st.columns(3)
        info_col1.metric("Subject", row["Pedagogy_Subject"])
        info_col2.metric("Prompt Type", row["Prompt_Type"])
        info_col3.metric("Current Score", f"{row['Total_Score']:.0f}/{MAX_SCORE_PER_TASK}")

        st.markdown("### Prompt")
        st.info(row["Prompt"])

        st.markdown("### Audio Response")

        audio_name = row["Voice_File_Name"]

        if audio_name in st.session_state.audio_files:
            audio_bytes = st.session_state.audio_files[audio_name]
            st.audio(audio_bytes)
        else:
            st.caption("Audio file is not available in this session. If using external data, keep the audio link or file separately.")

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
# Page 5: Score Responses
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
            task_list = sorted(
                student_df["Task_No"].dropna().unique(),
                key=clean_task_order
            )
            selected_task = st.selectbox("Select Task", task_list)

        idx = df[
            (df["Student_ID"] == selected_student) &
            (df["Task_No"] == selected_task)
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
                audio_bytes = st.session_state.audio_files[audio_name]
                st.audio(audio_bytes)
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
            suggested_feedback = generate_feedback(temp_row)
            st.info(suggested_feedback)

        if st.button("Save Scores and Feedback", type="primary"):
            for rubric_col, score in scores.items():
                df.loc[idx, rubric_col] = score

            df.loc[idx, "Feedback"] = feedback_text.strip()

            df = calculate_scores(df)
            st.session_state.data = df

            st.success("Scores and feedback saved successfully.")

        st.caption("Scoring guide: 1 = Very weak | 2 = Weak | 3 = Moderate | 4 = Good | 5 = Excellent")


# -------------------------------------------------------
# Page 6: Diagnostic Profile
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
        student_df = student_df.sort_values("Task_No", key=lambda x: x.map(clean_task_order))

        st.divider()

        st.subheader(f"Diagnostic Profile: {selected_student}")

        name_value = student_df["Name"].iloc[0] if "Name" in student_df.columns else ""
        semester_value = student_df["Semester"].iloc[0] if "Semester" in student_df.columns else ""
        subject_value = student_df["Pedagogy_Subject"].iloc[0] if "Pedagogy_Subject" in student_df.columns else ""

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

            ax2.plot(student_df["Task_No"], student_df["Total_Score"], marker="o")
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
# Page 7: Task Analytics
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
            df.groupby("Task_No")["Total_Score"]
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

        task_summary["Task_Order"] = task_summary["Task_No"].map(clean_task_order)
        task_summary = task_summary.sort_values("Task_Order")

        st.dataframe(task_summary.drop(columns=["Task_Order"]), use_container_width=True)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(task_summary["Task_No"], task_summary["Mean Score"])
        ax.set_xlabel("Task")
        ax.set_ylabel("Mean Total Score")
        ax.set_ylim(0, MAX_SCORE_PER_TASK)
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

        st.markdown("### Pedagogy Subject-wise Summary")

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

        st.markdown("### Completion Status")

        completion = (
            df.groupby(["Student_ID", "Name", "Semester", "Pedagogy_Subject"])["Task_No"]
            .count()
            .reset_index()
        )

        completion.rename(columns={"Task_No": "Tasks_Submitted"}, inplace=True)

        st.dataframe(completion, use_container_width=True)


# -------------------------------------------------------
# Page 8: Export Data
# -------------------------------------------------------

elif page == "Export Data":
    st.title("Export Data")

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
            "Important: In this testing version, audio files are stored only during the active app session. "
            "For real data collection, connect the app to cloud storage or ask participants to upload audio through Google Forms/Drive."
        )
