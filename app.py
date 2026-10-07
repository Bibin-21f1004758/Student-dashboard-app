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


# Function to fetch and clean data live from Google Sheets safely
@st.cache_data(ttl=60)  # Refreshes data automatically every 60 seconds
def load_google_sheet(s_id):
  url = f"https://docs.google.com/spreadsheets/d/{s_id}/export?format=csv"
  raw_df = pd.read_csv(url, header=None)

  # Find the row index where header terms ('Name' and 'Roll') are located safely
  header_row_idx = None
  for idx, row in raw_df.iterrows():
    # Convert row values to string safely, ignoring NaNs/floats
    row_str_values = [str(val) for val in row.values if pd.notna(val)]
    joined_row = " ".join(row_str_values)
    if "Name" in joined_row and ("Roll" in joined_row or "roll" in joined_row):
      header_row_idx = idx
      break

  if header_row_idx is not None:
    df = raw_df.iloc[header_row_idx + 1 :].copy()
    df.columns = raw_df.iloc[header_row_idx].values
    df = df.loc[:, df.columns.notna()]  # Drop NaN columns
    # Find name column dynamically to drop rows missing names
    cols = [str(c).strip() for c in df.columns]
    name_col = next((c for c in cols if "name" in c.lower()), cols[1] if len(cols) > 1 else cols[0])
    df = df.dropna(subset=[name_col])
    return df
  else:
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

    # Clean up column names representation
    df.columns = [str(c).strip() for c in df.columns]
    
    # Identify Name and Roll number columns dynamically
    name_col = next(
        (c for c in df.columns if "name" in c.lower()), df.columns[1]
    )
    roll_col = next(
        (c for c in df.columns if "roll" in c.lower()), df.columns[0]
    )

    st.markdown(f"### 📚 Class: `{selected_class}`")

    # Get all student names into the dropdown list
    student_names = df[name_col].dropna().astype(str).tolist()

    selected_student = st.selectbox(
        "🔍 Select Your Name from the List:",
        ["-- Please Select Your Name --"] + student_names,
    )

    if selected_student != "-- Please Select Your Name --":
      # Filter row for the chosen student
      student_row = df[df[name_col].astype(str) == selected_student].iloc[0]

      st.markdown("---")
      st.success(f"Displaying records for: **{selected_student}**")

      # Display key metric summary cards
      col1, col2, col3 = st.columns(3)
      with col1:
        roll_val = student_row.get(roll_col, "N/A")
        st.metric(label="Roll Number", value=str(roll_val))

      with col2:
        att_col = next(
            (c for c in df.columns if "att" in c.lower() and "%" in c), None
        )
        att_val = student_row.get(att_col, "N/A") if att_col else "N/A"
        st.metric(label="Attendance (%)", value=str(att_val))

      with col3:
        tot_col = next(
            (c for c in df.columns if "total" in c.lower()), None
        )
        tot_val = student_row.get(tot_col, "N/A") if tot_col else "N/A"
        st.metric(label="Total Mark", value=str(tot_val))

      # Display student's mark breakdown table
      st.markdown("#### 📋 Detailed Mark Breakdown")
      breakdown_df = pd.DataFrame(
          {
              "Component / Subject": student_row.index,
              "Marks Obtained": student_row.values,
          }
      )
      st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

  except Exception as e:
    st.error(
        "Could not load data from Google Drive. Verify that the sheet is shared"
        " publicly with **'Anyone with the link can view'** and the ID is"
        f" correct. Error details: {e}"
    )
