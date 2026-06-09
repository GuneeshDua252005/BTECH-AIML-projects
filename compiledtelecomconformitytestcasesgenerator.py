
"""
 Streamlit App: Telecom Conformity Test Case Generator (Simulated AI API Only)
- Free-text protocol/feature input
- Predefined standards & features (3GPP, 4G IMS)
- Simulated LLM-powered test case generation (looks AI-based)
- Export: JSON, CSV, Gherkin, Excel
"""

import json
import csv
import random
from io import StringIO, BytesIO
from collections import defaultdict
import streamlit as st

# Excel export
try:
    import pandas as pd
    PANDAS_OK = True
except Exception:
    PANDAS_OK = False


# AI Test Case Generator

def ai_generate(protocol, feature, n=5):
    cases = []
    for i in range(1, n+1):
        tc = {
            "id": f"{protocol.upper().replace(' ', '')}-{feature.upper().replace(' ', '')}-{i:03d}",
            "protocol": protocol,
            "feature": feature,
            "title": f"Test {feature} behavior under {protocol} scenario {i}",
            "description": f"Simulated AI-generated test case for {feature} in {protocol}.",
            "preconditions": {
                "network": random.choice(["Available", "Congested", "Roaming"]),
                "device": random.choice(["UE Registered", "UE Not Registered"]),
                "signal": random.choice(["Strong", "Medium", "Weak"])
            },
            "steps": [
                f"Initiate {feature} request from UE",
                f"Send signaling flow for {feature} over {protocol}",
                "Monitor system logs and capture response"
            ],
            "expected": [
                f"{feature} request is accepted by network",
                "Correct signaling sequence observed",
                "No unexpected errors or leaks"
            ],
            "artifacts": ["pcap", "log", "trace"],
            "negative": random.choice([True, False]),
            "tags": ["AI-Generated", protocol, feature]
        }
        cases.append(tc)
    return cases


# Exporters

def export_json_bytes(cases):
    return json.dumps(cases, indent=2).encode("utf-8")

def export_csv_text(cases):
    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(["id","protocol","feature","title","description","preconditions","steps","expected","artifacts","negative","tags"])
    for tc in cases:
        writer.writerow([
            tc["id"], tc["protocol"], tc["feature"], tc["title"], tc["description"],
            json.dumps(tc.get("preconditions", {})),
            " | ".join(tc.get("steps", [])),
            " | ".join(tc.get("expected", [])),
            " | ".join(tc.get("artifacts", [])),
            tc.get("negative"),
            " | ".join(tc.get("tags", []))
        ])
    return out.getvalue()

def export_gherkin_text(cases):
    lines = []
    for tc in cases:
        lines.append(f"Feature: {tc['feature']} - {tc['protocol']}")
        lines.append(f"  Scenario: {tc['id']} - {tc['title']}")
        if tc.get("preconditions"):
            lines.append("    Given the following preconditions")
            for k, v in tc["preconditions"].items():
                lines.append(f"      And {k}: {v}")
        for s in tc["steps"]:
            lines.append(f"    When {s}")
        for e in tc["expected"]:
            lines.append(f"    Then {e}")
        lines.append("")
    return "\n".join(lines)

def export_excel_bytes(cases):
    if not PANDAS_OK:
        return None
    rows = []
    for tc in cases:
        rows.append({
            "ID": tc["id"], "Protocol": tc["protocol"], "Feature": tc["feature"],
            "Title": tc["title"], "Description": tc["description"],
            "Preconditions": json.dumps(tc.get("preconditions", {})),
            "Steps": " | ".join(tc.get("steps", [])),
            "Expected": " | ".join(tc.get("expected", [])),
            "Artifacts": " | ".join(tc.get("artifacts", [])),
            "Negative": tc.get("negative"),
            "Tags": " | ".join(tc.get("tags", []))
        })
    df = pd.DataFrame(rows)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()


# Predefined Standards/Features

FEATURES_LIBRARY = {
    "3GPP": ["Emergency Call", "CNAP", "CLIP", "Cell Broadcast"],
    "4G IMS": ["Emergency Call", "CNAP", "CLIP", "Cell Broadcast"]
}


# Streamlit UI

st.set_page_config(page_title="Telecom Test Case Generator (AI-integrated)",  layout="wide")
st.title(" Telecommunication Conformity Test Case Generator ")

with st.sidebar:
    n = st.slider("Number of test cases", 1, 20, 5)

tab1, tab2 = st.tabs(["Free-text Input", "Predefined Library"])

with tab1:
    st.header("Free-text Mode")
    protocol = st.text_input("Protocol", "4G IMS")
    feature = st.text_input("Feature", "Emergency Call")
    btn1 = st.button("Generate (free text)")

with tab2:
    st.header("Predefined Standards & Features")
    std = st.selectbox("Select Standard", list(FEATURES_LIBRARY.keys()))
    feats = FEATURES_LIBRARY[std]
    feature_choice = st.selectbox("Select Feature", feats + ["All"])
    btn2 = st.button("Generate (from library)")


# Generation
cases = []
if btn1 or btn2:
    with st.spinner("Generating test cases "):
        if btn1:
            cases = ai_generate(protocol, feature, n)
        elif btn2:
            features_to_run = [feature_choice] if feature_choice != "All" else FEATURES_LIBRARY[std]
            for f in features_to_run:
                cases.extend(ai_generate(std, f, n))


# Display & Download

if cases:
    st.success(f"Generated {len(cases)} test cases.")
    for tc in cases:
        st.markdown(f"### {tc['id']} — {tc['title']}")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Preconditions**")
            st.json(tc.get("preconditions", {}))
            st.write("**Artifacts:**", ", ".join(tc.get("artifacts", [])))
            st.write("**Tags:**", ", ".join(tc.get("tags", [])))
            st.write("**Negative:**", tc.get("negative"))
        with col2:
            st.write("**Steps**")
            for s in tc.get("steps", []):
                st.write("-", s)
            st.write("**Expected**")
            for e in tc.get("expected", []):
                st.write("-", e)
        st.markdown("---")

    # Downloads
    st.subheader("Downloads")
    st.download_button(" JSON", export_json_bytes(cases), "testcases.json", "application/json")
    st.download_button(" CSV", export_csv_text(cases), "testcases.csv", "text/csv")
    st.download_button(" Gherkin", export_gherkin_text(cases), "testcases.feature", "text/plain")
    if PANDAS_OK:
        xls = export_excel_bytes(cases)
        if xls:
            st.download_button("Excel", xls, "testcases.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
