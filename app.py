import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="VoiceBridge-PST Analytics",
    page_icon="🎙️",
    layout="wide"
)

# -------------------------------------------------------
# Constants
# -------------------------------------------------------

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

RUBRIC_LABELS = {
    "Conceptual_Clarity": "Conceptual Clarity",
    "Pedagogical_Reasoning": "Pedagogical Reasoning",
    "Learner_Centred_Explanation": "Learner-Centred Explanation",
    "Misconception_Diagnosis": "Misconception Diagnosis",
    "Use_of_Example_Strategy": "Use of Example / Strategy",
    "Reflective_Thinking": "Reflective Thinking",
    "Voice_Written_Alignment": "Voice–Written Alignment"
}

MAX_SCORE_PER_TASK = len(RUBRIC_COLUMNS) * 5


# -------------------------------------------------------
# Helper Functions
# -------------------------------------------------------

def create_sample_template():
    data = {
        "Student_ID": ["PST01", "PST01", "PST02", "PST02"],
        "Group": ["Experimental", "Experimental", "Control", "Control"],
        "Task_No": ["Task 1", "Task 2", "Task 1", "Task 2"],
        "Prompt_Type": [
            "Misconception Diagnosis",
            "Classroom Response",
            "Misconception Diagnosis",
            "Classroom Response"
        ],
        "Prompt": [
            "A Class VI student says that a larger denominator means a larger fraction. How will you respond?",
            "Some students are not participating in group work. What will you do as a teacher?",
            "A Class VI student says that a larger denominator means a larger fraction. How will you respond?",
            "Some students are not participating in group work. What will you do as a teacher?"
        ],
        "Voice_File_Link": [
            "https://drive.google.com/example-audio-1",
            "https://drive.google.com/example-audio-2",
            "",
            ""
        ],
        "Written_Response": [
            "I will first identify the misconception and use visual fraction strips to explain.",
            "I will observe the reasons, assign roles, and encourage participation.",
            "I will explain fractions by giving examples.",
            "I will ask students to participate and write answers."
        ],
        "Reflection_1": [
            "The student is confused about denominator size and fraction value.",
            "Lack of role clarity may reduce participation.",
            "",
            ""
        ],
        "Reflection_2": [
            "I will use paper folding or fraction circles.",
            "I will use group roles and peer support.",
            "",
            ""
        ]
    }

    df = pd.DataFrame(data)

    for col in RUBRIC_COLUMNS:
        df[col] = np.nan

    return df


def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing


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
        "Conceptual_Clarity": "Strengthen clarity of the core pedagogical or conceptual issue before proposing a response.",
        "Pedagogical_Reasoning": "Provide a stronger justification for why the selected teaching response is appropriate.",
        "Learner_Centred_Explanation": "Connect the explanation more clearly with learners’ needs, level, and classroom context.",
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


def clean_task_order(task_value):
    try:
        return int(str(task_value).replace("Task", "").strip())
    except:
        return str(task_value)


def show_required_columns():
    st.code(
        """
Student_ID
Group
Task_No
Prompt_Type
Prompt
Voice_File_Link
Written_Response
Reflection_1
Reflection_2
        """,
        language="text"
    )


# -------------------------------------------------------
# Session State
# -------------------------------------------------------

if "data" not in st.session_state:
    st.session_state.data = None


# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

st.sidebar.title("🎙️ VoiceBridge-PST")
st.sidebar.caption("Researcher Workspace")

page = st.sidebar.radio(
    "Workspace Menu",
    [
        "Overview",
        "Upload Data",
        "Review Responses",
        "Score Responses",
        "Individual Profile",
        "Group Analytics",
        "Export Data"
    ]
)

st.sidebar.divider()

if st.session_state.data is not None:
    current_df = calculate_scores(st.session_state.data)
    st.sidebar.metric("Participants", current_df["Student_ID"].nunique())
    st.sidebar.metric("Responses", len(current_df))
else:
    st.sidebar.info("Upload response data to begin.")


# -------------------------------------------------------
# Page 1: Overview
# -------------------------------------------------------

if page == "Overview":
    st.title("VoiceBridge-PST Analytics Dashboard")
    st.subheader("Researcher Workspace for Pedagogical Reasoning Assessment")

    st.markdown(
        """
        This dashboard supports response review, rubric-based scoring, individual diagnostic profiling, 
        group-level analytics, and export of scored data.

        The dashboard is intended for researcher or teacher-educator use only.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Step 1", "Upload")
        st.caption("Upload response data")

    with col2:
        st.metric("Step 2", "Review")
        st.caption("Check audio and written responses")

    with col3:
        st.metric("Step 3", "Score")
        st.caption("Apply rubric scores")

    with col4:
        st.metric("Step 4", "Analyse")
        st.caption("View profiles and group trends")

    st.divider()

    st.markdown("### Required Data Format")
    show_required_columns()

    sample_df = create_sample_template()
    sample_excel = convert_df_to_excel(sample_df)

    st.download_button(
        label="Download Sample Excel Template",
        data=sample_excel,
        file_name="VoiceBridge_PST_Sample_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# -------------------------------------------------------
# Page 2: Upload Data
# -------------------------------------------------------

elif page == "Upload Data":
    st.title("Upload Data")

    st.markdown(
        """
        Upload the response dataset in Excel or CSV format.  
        The uploaded file should contain the required columns listed below.
        """
    )

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

            missing_cols = validate_columns(df)

            if missing_cols:
                st.error("The uploaded file is missing required columns:")
                st.write(missing_cols)
            else:
                for col in RUBRIC_COLUMNS:
                    if col not in df.columns:
                        df[col] = np.nan

                df = calculate_scores(df)
                st.session_state.data = df

                st.success("Data uploaded successfully.")

                col1, col2, col3 = st.columns(3)
                col1.metric("Participants", df["Student_ID"].nunique())
                col2.metric("Responses", len(df))
                col3.metric("Groups", df["Group"].nunique())

                st.markdown("### Data Preview")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.divider()

    st.markdown("### Use Sample Data")
    if st.button("Load Sample Data"):
        df = create_sample_template()
        df = calculate_scores(df)
        st.session_state.data = df
        st.success("Sample data loaded successfully.")
        st.dataframe(df, use_container_width=True)


# -------------------------------------------------------
# Page 3: Review Responses
# -------------------------------------------------------

elif page == "Review Responses":
    st.title("Review Responses")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = calculate_scores(st.session_state.data)

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
        info_col1.metric("Group", row["Group"])
        info_col2.metric("Prompt Type", row["Prompt_Type"])
        info_col3.metric("Current Score", f"{row['Total_Score']:.0f}/{MAX_SCORE_PER_TASK}")

        st.markdown("### Prompt")
        st.info(row["Prompt"])

        st.markdown("### Audio Response")
        if pd.notna(row["Voice_File_Link"]) and str(row["Voice_File_Link"]).strip() != "":
            st.markdown(f"[Open Audio Response]({row['Voice_File_Link']})")
        else:
            st.caption("No audio link available.")

        st.markdown("### Written Note")
        st.write(row["Written_Response"])

        st.markdown("### Reflections")
        ref_col1, ref_col2 = st.columns(2)

        with ref_col1:
            st.markdown("**Diagnostic Reflection**")
            if pd.notna(row["Reflection_1"]) and str(row["Reflection_1"]).strip() != "":
                st.write(row["Reflection_1"])
            else:
                st.caption("Not available.")

        with ref_col2:
            st.markdown("**Strategy Reflection**")
            if pd.notna(row["Reflection_2"]) and str(row["Reflection_2"]).strip() != "":
                st.write(row["Reflection_2"])
            else:
                st.caption("Not available.")

        st.markdown("### Existing Scores")
        score_display = {
            RUBRIC_LABELS[col]: row[col] if pd.notna(row[col]) else "Not scored"
            for col in RUBRIC_COLUMNS
        }
        st.table(pd.DataFrame(score_display.items(), columns=["Dimension", "Score"]))


# -------------------------------------------------------
# Page 4: Score Responses
# -------------------------------------------------------

elif page == "Score Responses":
    st.title("Score Responses")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = st.session_state.data.copy()

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
            if pd.notna(row["Voice_File_Link"]) and str(row["Voice_File_Link"]).strip() != "":
                st.markdown(f"[Open Audio Response]({row['Voice_File_Link']})")
            else:
                st.caption("No audio link available.")

            st.markdown("**Written Note**")
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

        if st.button("Save Scores", type="primary"):
            for rubric_col, score in scores.items():
                df.loc[idx, rubric_col] = score

            df = calculate_scores(df)
            st.session_state.data = df

            st.success("Scores saved successfully.")

        st.markdown("### Scoring Guide")
        st.caption(
            "1 = Very weak | 2 = Weak | 3 = Moderate | 4 = Good | 5 = Excellent"
        )


# -------------------------------------------------------
# Page 5: Individual Profile
# -------------------------------------------------------

elif page == "Individual Profile":
    st.title("Individual Profile")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = calculate_scores(st.session_state.data)

        student_ids = sorted(df["Student_ID"].dropna().unique())
        selected_student = st.selectbox("Select Student ID", student_ids)

        student_df = df[df["Student_ID"] == selected_student].copy()
        student_df = student_df.sort_values("Task_No", key=lambda x: x.map(clean_task_order))

        st.divider()

        st.subheader(f"Diagnostic Profile: {selected_student}")

        total_score = student_df["Total_Score"].sum()
        max_possible = len(student_df) * MAX_SCORE_PER_TASK
        overall_percentage = (total_score / max_possible) * 100 if max_possible else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Group", student_df["Group"].iloc[0])
        col2.metric("Total Score", f"{total_score:.0f}/{max_possible}")
        col3.metric("Overall %", f"{overall_percentage:.2f}%")
        col4.metric("Tasks", len(student_df))

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

        st.markdown("### Individual Data")
        st.dataframe(student_df, use_container_width=True)


# -------------------------------------------------------
# Page 6: Group Analytics
# -------------------------------------------------------

elif page == "Group Analytics":
    st.title("Group Analytics")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = calculate_scores(st.session_state.data)

        st.subheader("Dataset Summary")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Participants", df["Student_ID"].nunique())
        col2.metric("Responses", len(df))
        col3.metric("Groups", df["Group"].nunique())
        col4.metric("Average Score", f"{df['Total_Score'].mean():.2f}")

        st.divider()

        st.markdown("### Group-wise Score Summary")

        group_summary = (
            df.groupby("Group")["Total_Score"]
            .agg(["mean", "std", "count"])
            .reset_index()
        )

        group_summary.rename(
            columns={
                "mean": "Mean Score",
                "std": "SD",
                "count": "Responses"
            },
            inplace=True
        )

        st.dataframe(group_summary, use_container_width=True)

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(group_summary["Group"], group_summary["Mean Score"])
        ax.set_ylabel("Mean Total Score")
        ax.set_ylim(0, MAX_SCORE_PER_TASK)
        st.pyplot(fig)

        st.markdown("### Task-wise Progress by Group")

        task_group_summary = (
            df.groupby(["Task_No", "Group"])["Total_Score"]
            .mean()
            .reset_index()
        )

        task_group_summary["Task_Order"] = task_group_summary["Task_No"].map(clean_task_order)
        task_group_summary = task_group_summary.sort_values("Task_Order")

        fig2, ax2 = plt.subplots(figsize=(8, 4))

        for group in task_group_summary["Group"].unique():
            group_data = task_group_summary[task_group_summary["Group"] == group]
            ax2.plot(
                group_data["Task_No"],
                group_data["Total_Score"],
                marker="o",
                label=group
            )

        ax2.set_xlabel("Task")
        ax2.set_ylabel("Mean Total Score")
        ax2.set_ylim(0, MAX_SCORE_PER_TASK)
        ax2.legend()
        ax2.tick_params(axis="x", rotation=45)
        st.pyplot(fig2)

        st.markdown("### Dimension-wise Group Profile")

        rubric_mean = (
            df.groupby("Group")[RUBRIC_COLUMNS]
            .mean(numeric_only=True)
            .reset_index()
        )

        st.dataframe(rubric_mean, use_container_width=True)

        selected_group = st.selectbox(
            "Select group for dimension chart",
            rubric_mean["Group"].unique()
        )

        group_row = rubric_mean[rubric_mean["Group"] == selected_group].iloc[0]
        labels = [RUBRIC_LABELS[col] for col in RUBRIC_COLUMNS]
        values = [group_row[col] for col in RUBRIC_COLUMNS]

        fig3, ax3 = plt.subplots(figsize=(10, 5))
        ax3.bar(labels, values)
        ax3.set_ylabel("Average Score")
        ax3.set_ylim(0, 5)
        ax3.tick_params(axis="x", rotation=75)
        st.pyplot(fig3)

        st.markdown("### Completion Status")

        completion = (
            df.groupby(["Student_ID", "Group"])["Task_No"]
            .count()
            .reset_index()
        )

        completion.rename(columns={"Task_No": "Tasks_Submitted"}, inplace=True)
        st.dataframe(completion, use_container_width=True)


# -------------------------------------------------------
# Page 7: Export Data
# -------------------------------------------------------

elif page == "Export Data":
    st.title("Export Data")

    if st.session_state.data is None:
        st.warning("Please upload data first.")
    else:
        df = calculate_scores(st.session_state.data)

        st.markdown("Download the scored dataset for further statistical analysis.")

        csv_data = df.to_csv(index=False).encode("utf-8")
        excel_data = convert_df_to_excel(df)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="VoiceBridge_PST_Scored_Data.csv",
                mime="text/csv"
            )

        with col2:
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name="VoiceBridge_PST_Scored_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.markdown("### Data Preview")
        st.dataframe(df, use_container_width=True)
