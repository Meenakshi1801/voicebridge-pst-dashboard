import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(
    page_title="VoiceBridge-PST Dashboard",
    page_icon="🎙️",
    layout="wide"
)

# -----------------------------
# Helper Functions
# -----------------------------

REQUIRED_COLUMNS = [
    "Student_ID",
    "Group",
    "Task_No",
    "Prompt_Type",
    "Prompt",
    "Voice_File_Link",
    "Written_Response",
    "Reflection_1",
    "Reflection_2"
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

MAX_SCORE_PER_TASK = len(RUBRIC_COLUMNS) * 5


def create_sample_template():
    data = {
        "Student_ID": ["PST01", "PST01", "PST02"],
        "Group": ["Experimental", "Experimental", "Control"],
        "Task_No": ["Task 1", "Task 2", "Task 1"],
        "Prompt_Type": ["Misconception Diagnosis", "Classroom Response", "Misconception Diagnosis"],
        "Prompt": [
            "A Class VI student says that a larger denominator means a larger fraction. How will you respond?",
            "Some students are not participating in group work. What will you do as a teacher?",
            "A Class VI student says that a larger denominator means a larger fraction. How will you respond?"
        ],
        "Voice_File_Link": [
            "https://drive.google.com/example-audio-1",
            "https://drive.google.com/example-audio-2",
            ""
        ],
        "Written_Response": [
            "I will first identify the misconception and use visual fraction strips to explain.",
            "I will observe the reasons, assign roles, and encourage participation.",
            "I will explain fractions by giving examples."
        ],
        "Reflection_1": [
            "The student is confused about denominator size.",
            "Lack of role clarity may reduce participation.",
            "The student does not understand denominator."
        ],
        "Reflection_2": [
            "I will use paper folding or fraction circles.",
            "I will use group roles and peer support.",
            "I will use examples on the board."
        ]
    }
    return pd.DataFrame(data)


def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing


def calculate_scores(df):
    existing_rubric_cols = [col for col in RUBRIC_COLUMNS if col in df.columns]

    if existing_rubric_cols:
        df["Total_Score"] = df[existing_rubric_cols].sum(axis=1)
        df["Percentage"] = (df["Total_Score"] / MAX_SCORE_PER_TASK) * 100
    else:
        df["Total_Score"] = 0
        df["Percentage"] = 0

    return df


def generate_feedback(row):
    dimension_scores = {col: row[col] for col in RUBRIC_COLUMNS if col in row.index}

    if not dimension_scores:
        return "No rubric scores available."

    strongest = max(dimension_scores, key=dimension_scores.get)
    weakest = min(dimension_scores, key=dimension_scores.get)

    feedback_map = {
        "Conceptual_Clarity": "Improve clarity of the core concept before proposing a teaching response.",
        "Pedagogical_Reasoning": "Give stronger justification for why a particular teaching strategy is suitable.",
        "Learner_Centred_Explanation": "Make the explanation more learner-centred and connected to student needs.",
        "Misconception_Diagnosis": "Identify the exact misconception or learning difficulty more clearly.",
        "Use_of_Example_Strategy": "Use more concrete examples, activities, or classroom strategies.",
        "Reflective_Thinking": "Add deeper reflection on strengths, limitations, and possible improvements.",
        "Voice_Written_Alignment": "Ensure that the written response clearly follows the oral explanation."
    }

    return (
        f"Strongest area: {strongest.replace('_', ' ')}. "
        f"Needs improvement: {weakest.replace('_', ' ')}. "
        f"Suggestion: {feedback_map.get(weakest, 'Continue improving pedagogical reasoning.')}"
    )


def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="VoiceBridge_PST_Data")
    return output.getvalue()


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("🎙️ VoiceBridge-PST")
page = st.sidebar.radio(
    "Dashboard Menu",
    [
        "About Model",
        "Upload Data",
        "Response Viewer",
        "Rubric Scoring",
        "Student Profile",
        "Group Analytics",
        "Download Report"
    ]
)

# Session state for data
if "data" not in st.session_state:
    st.session_state.data = None

# -----------------------------
# Page 1: About Model
# -----------------------------

if page == "About Model":
    st.title("VoiceBridge-PST Dashboard")
    st.subheader("A Diagnostic Analytics Tool for Micro-Pedagogical Reasoning")

    st.markdown("""
    **VoiceBridge-PST** is a voice-first process-oriented assessment model for B.Ed. students / pre-service teachers.

    The model assesses how pre-service teachers think, explain, justify, and reflect on short classroom-based pedagogical situations.

    ### Model Flow

    **Pedagogical Prompt → Voice Response → Written Response → Reflection → Rubric Scoring → Diagnostic Feedback**

    ### Assessment Dimensions

    1. Conceptual Clarity  
    2. Pedagogical Reasoning  
    3. Learner-Centred Explanation  
    4. Misconception Diagnosis  
    5. Use of Example / Teaching Strategy  
    6. Reflective Thinking  
    7. Voice–Written Alignment  
    """)

    st.info("This dashboard is designed for researcher-supported scoring. It does not automatically score students.")

    sample_df = create_sample_template()
    excel_file = convert_df_to_excel(sample_df)

    st.download_button(
        label="Download Sample Data Template",
        data=excel_file,
        file_name="VoiceBridge_PST_Sample_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -----------------------------
# Page 2: Upload Data
# -----------------------------

elif page == "Upload Data":
    st.title("Upload Response Data")

    st.markdown("""
    Upload an Excel or CSV file containing student responses.

    Required columns:

    `Student_ID, Group, Task_No, Prompt_Type, Prompt, Voice_File_Link, Written_Response, Reflection_1, Reflection_2`
    """)

    uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            missing_cols = validate_columns(df)

            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
            else:
                for col in RUBRIC_COLUMNS:
                    if col not in df.columns:
                        df[col] = np.nan

                df = calculate_scores(df)
                st.session_state.data = df

                st.success("Data uploaded successfully.")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.markdown("### Or use sample data")
    if st.button("Load Sample Data"):
        df = create_sample_template()

        for col in RUBRIC_COLUMNS:
            df[col] = np.nan

        df = calculate_scores(df)
        st.session_state.data = df
        st.success("Sample data loaded.")
        st.dataframe(df, use_container_width=True)

# -----------------------------
# Page 3: Response Viewer
# -----------------------------

elif page == "Response Viewer":
    st.title("Response Viewer")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = st.session_state.data

        student_ids = sorted(df["Student_ID"].dropna().unique())
        selected_student = st.selectbox("Select Student", student_ids)

        student_df = df[df["Student_ID"] == selected_student]

        task_list = sorted(student_df["Task_No"].dropna().unique())
        selected_task = st.selectbox("Select Task", task_list)

        row = student_df[student_df["Task_No"] == selected_task].iloc[0]

        st.subheader(f"{selected_student} - {selected_task}")

        st.markdown(f"**Group:** {row['Group']}")
        st.markdown(f"**Prompt Type:** {row['Prompt_Type']}")
        st.markdown(f"**Prompt:** {row['Prompt']}")

        st.markdown("### Voice Response")
        if pd.notna(row["Voice_File_Link"]) and str(row["Voice_File_Link"]).strip() != "":
            st.markdown(f"[Open Voice File]({row['Voice_File_Link']})")
        else:
            st.info("No voice file link available.")

        st.markdown("### Written Response")
        st.write(row["Written_Response"])

        st.markdown("### Reflection")
        st.write("**Reflection 1:**", row["Reflection_1"])
        st.write("**Reflection 2:**", row["Reflection_2"])

# -----------------------------
# Page 4: Rubric Scoring
# -----------------------------

elif page == "Rubric Scoring":
    st.title("Rubric Scoring")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = st.session_state.data

        student_ids = sorted(df["Student_ID"].dropna().unique())
        selected_student = st.selectbox("Select Student", student_ids)

        student_df = df[df["Student_ID"] == selected_student]

        task_list = sorted(student_df["Task_No"].dropna().unique())
        selected_task = st.selectbox("Select Task", task_list)

        idx = df[(df["Student_ID"] == selected_student) & (df["Task_No"] == selected_task)].index[0]
        row = df.loc[idx]

        st.markdown(f"### Scoring: {selected_student} - {selected_task}")
        st.markdown(f"**Prompt:** {row['Prompt']}")

        with st.expander("View Student Response"):
            st.markdown("**Written Response:**")
            st.write(row["Written_Response"])

            st.markdown("**Reflection 1:**")
            st.write(row["Reflection_1"])

            st.markdown("**Reflection 2:**")
            st.write(row["Reflection_2"])

            if pd.notna(row["Voice_File_Link"]) and str(row["Voice_File_Link"]).strip() != "":
                st.markdown(f"[Open Voice File]({row['Voice_File_Link']})")

        st.markdown("### Rubric Scores")

        scores = {}
        col1, col2 = st.columns(2)

        for i, rubric_col in enumerate(RUBRIC_COLUMNS):
            current_value = row[rubric_col]
            if pd.isna(current_value):
                current_value = 3
            else:
                current_value = int(current_value)

            target_col = col1 if i % 2 == 0 else col2

            with target_col:
                scores[rubric_col] = st.slider(
                    rubric_col.replace("_", " "),
                    min_value=1,
                    max_value=5,
                    value=current_value,
                    key=f"{selected_student}_{selected_task}_{rubric_col}"
                )

        if st.button("Save Scores"):
            for rubric_col, score in scores.items():
                df.loc[idx, rubric_col] = score

            df = calculate_scores(df)
            st.session_state.data = df

            st.success("Scores saved successfully.")

        total_score = sum(scores.values())
        percentage = (total_score / MAX_SCORE_PER_TASK) * 100

        st.metric("Total Score", f"{total_score}/{MAX_SCORE_PER_TASK}")
        st.metric("Percentage", f"{percentage:.2f}%")

# -----------------------------
# Page 5: Student Profile
# -----------------------------

elif page == "Student Profile":
    st.title("Student Diagnostic Profile")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = calculate_scores(st.session_state.data)

        student_ids = sorted(df["Student_ID"].dropna().unique())
        selected_student = st.selectbox("Select Student", student_ids)

        student_df = df[df["Student_ID"] == selected_student].copy()

        st.subheader(f"Diagnostic Profile: {selected_student}")

        total_score = student_df["Total_Score"].sum()
        max_possible = len(student_df) * MAX_SCORE_PER_TASK
        overall_percentage = (total_score / max_possible) * 100 if max_possible else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Score", f"{total_score}/{max_possible}")
        col2.metric("Overall Percentage", f"{overall_percentage:.2f}%")
        col3.metric("Tasks Completed", len(student_df))

        rubric_means = student_df[RUBRIC_COLUMNS].mean(numeric_only=True)

        if rubric_means.notna().sum() > 0:
            strongest = rubric_means.idxmax()
            weakest = rubric_means.idxmin()

            st.markdown(f"**Strongest Dimension:** {strongest.replace('_', ' ')}")
            st.markdown(f"**Needs Improvement:** {weakest.replace('_', ' ')}")

            st.markdown("### Dimension-wise Profile")
            fig, ax = plt.subplots()
            ax.bar(rubric_means.index.str.replace("_", " "), rubric_means.values)
            ax.set_ylabel("Average Score")
            ax.set_ylim(0, 5)
            ax.tick_params(axis='x', rotation=75)
            st.pyplot(fig)

            st.markdown("### Task-wise Progress")
            fig2, ax2 = plt.subplots()
            ax2.plot(student_df["Task_No"], student_df["Total_Score"], marker="o")
            ax2.set_xlabel("Task")
            ax2.set_ylabel("Total Score")
            ax2.set_ylim(0, MAX_SCORE_PER_TASK)
            ax2.tick_params(axis='x', rotation=45)
            st.pyplot(fig2)

            st.markdown("### Diagnostic Feedback")
            latest_row = student_df.iloc[-1]
            st.info(generate_feedback(latest_row))
        else:
            st.info("Rubric scores are not available yet.")

        st.markdown("### Student Data")
        st.dataframe(student_df, use_container_width=True)

# -----------------------------
# Page 6: Group Analytics
# -----------------------------

elif page == "Group Analytics":
    st.title("Group Analytics")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = calculate_scores(st.session_state.data)

        st.subheader("Overall Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Participants", df["Student_ID"].nunique())
        col2.metric("Total Responses", len(df))
        col3.metric("Average Score", f"{df['Total_Score'].mean():.2f}")

        st.markdown("### Experimental vs Control Group")

        group_summary = df.groupby("Group")["Total_Score"].agg(["mean", "std", "count"]).reset_index()
        st.dataframe(group_summary, use_container_width=True)

        fig, ax = plt.subplots()
        ax.bar(group_summary["Group"], group_summary["mean"])
        ax.set_ylabel("Mean Total Score")
        ax.set_title("Group-wise Mean Score")
        st.pyplot(fig)

        st.markdown("### Task-wise Progress by Group")

        task_group_summary = df.groupby(["Task_No", "Group"])["Total_Score"].mean().reset_index()

        fig2, ax2 = plt.subplots()

        for group in task_group_summary["Group"].unique():
            group_data = task_group_summary[task_group_summary["Group"] == group]
            ax2.plot(group_data["Task_No"], group_data["Total_Score"], marker="o", label=group)

        ax2.set_xlabel("Task")
        ax2.set_ylabel("Mean Total Score")
        ax2.set_ylim(0, MAX_SCORE_PER_TASK)
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)

        st.markdown("### Dimension-wise Mean Scores")

        rubric_mean = df.groupby("Group")[RUBRIC_COLUMNS].mean(numeric_only=True).reset_index()
        st.dataframe(rubric_mean, use_container_width=True)

        selected_group = st.selectbox("Select Group for Dimension Chart", rubric_mean["Group"].unique())
        group_row = rubric_mean[rubric_mean["Group"] == selected_group].iloc[0]

        values = [group_row[col] for col in RUBRIC_COLUMNS]

        fig3, ax3 = plt.subplots()
        ax3.bar([col.replace("_", " ") for col in RUBRIC_COLUMNS], values)
        ax3.set_ylabel("Average Score")
        ax3.set_ylim(0, 5)
        ax3.tick_params(axis='x', rotation=75)
        st.pyplot(fig3)

        st.markdown("### Completion Status")

        completion = df.groupby(["Student_ID", "Group"])["Task_No"].count().reset_index()
        completion.rename(columns={"Task_No": "Tasks_Submitted"}, inplace=True)
        st.dataframe(completion, use_container_width=True)

# -----------------------------
# Page 7: Download Report
# -----------------------------

elif page == "Download Report":
    st.title("Download Report")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = calculate_scores(st.session_state.data)

        st.markdown("Download the scored dataset after rubric scoring.")

        csv = df.to_csv(index=False).encode("utf-8")
        excel = convert_df_to_excel(df)

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="VoiceBridge_PST_Scored_Data.csv",
            mime="text/csv"
        )

        st.download_button(
            label="Download Excel",
            data=excel,
            file_name="VoiceBridge_PST_Scored_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("### Preview")
        st.dataframe(df, use_container_width=True)
