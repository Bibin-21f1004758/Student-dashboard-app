import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Fundamentals of Engineering Mathematics - Internal Marks",
    page_icon="🎓",
    layout="wide",
)



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


# Function to fetch data live from Google Sheets safely
@st.cache_data(ttl=60)  # Refreshes data automatically every 60 seconds
def load_google_sheet(s_id):
  url = f"https://docs.google.com/spreadsheets/d/{s_id}/export?format=csv"
  raw_df = pd.read_csv(url, header=None)

  # Extract top title rows (rows 0 to 3 if present)
  titles = []
  for i in range(min(4, len(raw_df))):
    val = raw_df.iloc[i, 0]
    if pd.notna(val) and str(val).strip() != "":
      titles.append(str(val).strip())

  # Find the row index where header terms ('Name' and 'Roll') are located
  header_row_idx = None
  for idx, row in raw_df.iterrows():
    row_str_values = [str(val) for val in row.values if pd.notna(val)]
    joined_row = " ".join(row_str_values)
    if "Name" in joined_row and ("Roll" in joined_row or "roll" in joined_row):
      header_row_idx = idx
      break

  if header_row_idx is not None:
    df = raw_df.iloc[header_row_idx + 1 :].copy()
    df.columns = raw_df.iloc[header_row_idx].values
    df = df.loc[:, df.columns.notna()]  # Drop NaN columns
    df.columns = [str(c).strip() for c in df.columns]
    name_col = next((c for c in df.columns if "name" in c.lower()), "Name")
    df = df.dropna(subset=[name_col])
    df = df[df[name_col].astype(str).str.lower() != "name"]
    return df, titles
  else:
    return pd.read_csv(url), titles


# Verify if IDs are configured
if "YOUR_" in sheet_id:
  st.warning(
      f"⚠️ Please update the Google Sheet ID for **{selected_class}** in your"
      " `app.py` script."
  )
else:
  try:
    df, titles = load_google_sheet(sheet_id)

    # Display Sheet Headings matching your spreadsheet layout
    if len(titles) > 0:
      st.markdown(
          f"<h2 style='text-align: center; color: #4F46E5;'>{titles[0]}</h2>",
          unsafe_allow_html=True,
      )
      for t in titles[1:]:
        st.markdown(
            f"<h4 style='text-align: center; color: #6B7280;'>{t}</h4>",
            unsafe_allow_html=True,
        )
    else:
      st.title("🎓 Government Polytechnic College, Nedumkandam")
      st.subheader(f"Internal Marks Portal - {selected_class}")

    st.markdown("---")

    # Clean up column names representation
    df.columns = [str(c).strip() for c in df.columns]

    # Identify Name and Roll number columns dynamically
    name_col = next(
        (c for c in df.columns if "name" in c.lower()), "Name"
    )
    roll_col = next(
        (c for c in df.columns if "roll" in c.lower()), "Roll number"
    )

    # Get clean list of all student names
    student_names = df[name_col].dropna().astype(str).tolist()
    student_names = [name for name in student_names if name.strip() != ""]

    selected_student = st.selectbox(
        "🔍 Select Your Name from the List:",
        ["-- Please Select Your Name --"] + student_names,
    )

    if selected_student != "-- Please Select Your Name --":
      # Filter row for the chosen student
      student_row = df[df[name_col].astype(str) == selected_student].iloc[0]

      st.markdown("---")
      st.success(f"Displaying records for: **{selected_student}**")

      # Map horizontal row data into the vertical Student View card format
      vertical_data = {
          "Mark Component": [
              "Roll Number",
              "Student Name",
              "CA1 / Self Learning-1 (15)",
              "CA2 / Self Learning-2 (15)",
              "CA3 / Self Learning-3 (15)",
              "CA4 / Self Learning-4 (15)",
              "CA5 / SERIES-1 (50)",
              "CA6 / SERIES-2 (50)",
              "SERIES-1 CONVERTED (20)",
              "SERIES-2 CONVERTED (20)",
              "ATTENDANCE (%)",
              "ATTENDANCE (5)",
              "SELF LEARNING (15)",
              "SERIES (20)",
              "TOTAL (40)",
          ],
          "Mark / Details": [
              student_row.get(roll_col, "N/A"),
              student_row.get(name_col, "N/A"),
              student_row.get("SL-1(15)", student_row.get("SL-1 (15)", "N/A")),
              student_row.get("SL-2(15)", student_row.get("SL-2 (15)", "N/A")),
              student_row.get("SL-3(15)", student_row.get("SL-3 (15)", "N/A")),
              student_row.get("SL-4(15)", student_row.get("SL-4 (15)", "N/A")),
              student_row.get(
                  "SERIES-1(50)", student_row.get("SERIES-1 (50)", "N/A")
              ),
              student_row.get(
                  "SERIES-2(50)", student_row.get("SERIES-2 (50)", "N/A")
              ),
              student_row.get(
                  "SERIES-1 CONVERTED(20)",
                  student_row.get("SERIES-1 CONVERTED (20)", "N/A"),
              ),
              student_row.get(
                  "SERIES-2 CONVERTED(20)",
                  student_row.get("SERIES-2 CONVERTED (20)", "N/A"),
              ),
              student_row.get(
                  "ATTENDANCE(%)", student_row.get("ATTENDANCE (%)", "N/A")
              ),
              student_row.get(
                  "ATTENDANCE(5)", student_row.get("ATTENDANCE (5)", "N/A")
              ),
              student_row.get(
                  "SELF LEARNING(15)",
                  student_row.get("SELF LEARNING (15)", "N/A"),
              ),
              student_row.get("SERIES(20)", student_row.get("SERIES (20)", "N/A")),
              student_row.get("TOTAL(40)", student_row.get("TOTAL (40)", "N/A")),
          ],
      }

      vertical_df = pd.DataFrame(vertical_data)

      # Display the vertical mark sheet table matching your reference screenshot headers
      st.markdown("#### 📋 Student Mark Splitup")
      st.dataframe(vertical_df, use_container_width=True, hide_index=True)

  except Exception as e:
    st.error(
        "Could not load data from Google Drive. Verify that the sheet is shared"
        " publicly with **'Anyone with the link can view'** and the ID is"
        f" correct. Error details: {e}"
    )
