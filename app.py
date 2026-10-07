import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="GPTC Nedumkandam - Internal Marks Portal",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Government Polytechnic College, Nedumkandam")
st.subheader("Department Internal Marks Portal")

# ---------------------------------------------------------
# CONFIGURATION: Map your classes to their Google Sheet IDs
# ---------------------------------------------------------
CLASS_SHEETS = {
    "CST (Computer Science & Technology)": "1WzhjZGVtoPZqdh9bNYu-A9TbeLj8xDVd0I4BM8EyoUA",
    "CT (Computer Engineering)": "1C_dw-gsFMXcUiHLNI_g-T3wVcsjcLbwakc9rDoigN5I",
    "EL (Electronics Engineering)": "14spEFMoW9nDF7ierOQSzUYlcLemh53hH5ksGdqqa9lk",
}

# Sidebar: Class selection
st.sidebar.header("Student Portal")
selected_class = st.sidebar.selectbox("Select Your Class", list(CLASS_SHEETS.keys()))
sheet_id = CLASS_SHEETS[selected_class]


# Function to fetch data live from Google Sheets CSV export link
@st.cache_data(ttl=60)  # Refreshes data automatically every 60 seconds
def load_google_sheet(s_id):
  url = f"https://docs.google.com/spreadsheets/d/{s_id}/export?format=csv"
  return pd.read_csv(url)


# Verify if IDs are configured
if "YOUR_" in sheet_id:
  st.warning(
      f"⚠️ Please update the Google Sheet ID for **{selected_class}** in your"
      " `app.py` script."
  )
else:
  try:
    df = load_google_sheet(sheet_id)

    # Detect name and roll number columns automatically
    name_column = (
        "Name"
        if "Name" in df.columns
        else (df.columns[1] if len(df.columns) > 1 else df.columns[0])
    )
    roll_column = (
        "Roll number"
        if "Roll number" in df.columns
        else ("Roll Number" if "Roll Number" in df.columns else df.columns[0])
    )

    st.markdown(f"### 📚 Class: `{selected_class}`")

    # Dropdown to select student name
    student_names = df[name_column].dropna().tolist()
    selected_student = st.selectbox(
        "🔍 Select Your Name from the List:",
        ["-- Please Select Your Name --"] + student_names,
    )

    if selected_student != "-- Please Select Your Name --":
      student_row = df[df[name_column] == selected_student].iloc[0]

      st.markdown("---")
      st.success(f"Displaying records for: **{selected_student}**")

      # Metrics Row
      col1, col2, col3 = st.columns(3)
      with col1:
        st.metric(label="Roll Number", value=str(student_row.get(roll_column, "N/A")))
      with col2:
        att_val = "N/A"
        for col in df.columns:
          if "ATTENDANCE" in col.upper() and "%" in col:
            att_val = student_row.get(col, "N/A")
        st.metric(label="Attendance (%)", value=str(att_val))
      with col3:
        tot_val = "N/A"
        for col in df.columns:
          if "TOTAL" in col.upper():
            tot_val = student_row.get(col, "N/A")
        st.metric(label="Total Mark", value=str(tot_val))

      # Mark Breakdown Table
      st.markdown("#### 📋 Detailed Mark Breakdown")
      breakdown_df = pd.DataFrame(
          {
              "Component / Subject": student_row.index,
              "Marks / Details": student_row.values,
          }
      )
      st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

  except Exception as e:
    st.error(
        "Could not load data from Google Drive. Verify that the sheet is shared"
        " publicly with **'Anyone with the link can view'** and the ID is"
        f" correct. Error details: {e}"
    )
