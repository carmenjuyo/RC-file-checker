import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import tempfile
import os

st.title("XML Reservation Filter and Export to CSV")

# Upload XML files
uploaded_files = st.file_uploader("Upload XML files", type="xml", accept_multiple_files=True)

# Optional EI filter
ei_input = st.text_input("Filter by EI (comma-separated, optional):")
ei_values = [val.strip() for val in ei_input.split(",") if val.strip()]

# Required date filters
start_date = st.date_input("Start Date (TBD or later)")
end_date = st.date_input("End Date (TED or earlier)")

results = []

if uploaded_files and start_date and end_date:
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            tree = ET.parse(tmp_path)
            root = tree.getroot()
        except Exception as e:
            st.error(f"Error parsing file {uploaded_file.name}: {e}")
            continue
        finally:
            os.unlink(tmp_path)

        for rc in root.findall(".//RC"):
            attributes = rc.attrib
            ei = attributes.get("EI")
            tbd = attributes.get("TBD")
            ted = attributes.get("TED")

            if tbd and ted:
                try:
                    tbd_date = datetime.strptime(tbd, "%d-%b-%Y")
                    ted_date = datetime.strptime(ted, "%d-%b-%Y")

                    if start_date <= tbd_date.date() and ted_date.date() <= end_date:
                        if not ei_values or ei in ei_values:
                            results.append(attributes)
                except Exception as e:
                    st.warning(f"Skipping entry due to date format error in {uploaded_file.name}: {e}")

    # Output
    if results:
        df = pd.DataFrame(results)
        st.success(f"{len(results)} matching records found.")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="filtered_reservations.csv",
            mime="text/csv"
        )
    else:
        st.warning("No matching records found.")
