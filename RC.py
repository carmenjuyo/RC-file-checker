import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import tempfile
import os

st.title("XML Reservation Filter & CSV Export")

uploaded_files = st.file_uploader("Upload XML files", type="xml", accept_multiple_files=True)

ei_input = st.text_input("Filter by EI (comma-separated, optional):")
ei_values = [val.strip() for val in ei_input.split(",") if val.strip()]

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("TBD After (optional)", value=None)
with col2:
    end_date = st.date_input("TED Before (optional)", value=None)

stay_date = st.date_input("Stay Date (must be between TBD and TED, optional)", value=None)

results = []

if uploaded_files:
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

            try:
                tbd_date = datetime.strptime(tbd, "%d-%b-%Y").date() if tbd else None
                ted_date = datetime.strptime(ted, "%d-%b-%Y").date() if ted else None
            except Exception as e:
                st.warning(f"Skipping due to date format error in {uploaded_file.name}: {e}")
                continue

            # Apply filters only if provided
            match_ei = not ei_values or (ei and ei in ei_values)
            match_start = not start_date or (tbd_date and tbd_date >= start_date)
            match_end = not end_date or (ted_date and ted_date <= end_date)
            match_stay = not stay_date or (tbd_date and ted_date and tbd_date <= stay_date <= ted_date)

            if match_ei and match_start and match_end and match_stay:
                results.append(attributes)

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
