import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import tempfile

st.title("XML Reservation Filter")

uploaded_files = st.file_uploader("Upload XML files", type="xml", accept_multiple_files=True)

ei_input = st.text_input("Enter EI IDs (comma-separated):")
start_date = st.date_input("Start TBD date")
end_date = st.date_input("End TED date")

ei_values = [val.strip() for val in ei_input.split(",") if val.strip()]

if uploaded_files and ei_values and start_date and end_date:
    st.subheader("Filtered Results")
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        tree = ET.parse(tmp_path)
        root = tree.getroot()
        os.unlink(tmp_path)

        for rc in root.findall(".//RC"):
            ei = rc.get("EI")
            tbd = rc.get("TBD")
            ted = rc.get("TED")

            if ei in ei_values and tbd and ted:
                try:
                    tbd_date = datetime.strptime(tbd, "%d-%b-%Y")
                    ted_date = datetime.strptime(ted, "%d-%b-%Y")
                    if start_date <= tbd_date.date() and ted_date.date() <= end_date:
                        st.code(ET.tostring(rc, encoding="unicode"), language="xml")
                except Exception as e:
                    st.error(f"Error parsing date in file {uploaded_file.name}: {e}")
