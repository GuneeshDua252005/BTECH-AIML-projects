import streamlit as st
import pandas as pd
import requests
import os
from io import BytesIO
import requests

url = "https://api-inference.huggingface.co/models/bigscience/bloomz-7b1-mt"
headers = {"Authorization": "Bearer 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"}

try:
    r = requests.get(url, headers=headers, timeout=5)
    print(r.status_code, r.text)
except Exception as e:
    print("Connection failed:", e)


# Set your Hugging Face API token
HF_API_TOKEN = "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"
HF_MODEL = "bigscience/bloomz-7b1-mt"  # Example model

# Function to call HF LLM for generating test cases
def generate_test_case(feature, standard):
    prompt = f"Generate a detailed conformity test case for the telecommunication feature '{feature}' under the standard '{standard}'. Include preconditions, test steps, and expected outcomes in structured format."
    
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 300}
    }
    
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        # Extract text from model output
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        else:
            return str(result)
    else:
        return f"Error: {response.status_code} - {response.text}"

# Streamlit UI
st.title("Telecom Conformity Test Case Generator")
st.markdown("Generate test cases for 3GPP and 4G IMS standards using AI.")

# Standard selection
standard = st.selectbox("Select Standard", ["3GPP", "4G IMS"])

# Predefined features
predefined_features = ["Emergency Call", "Cell Broadcast", "CNAP", "CLIP", "SMS", "VoLTE", "VoWiFi"]
selected_features = st.multiselect("Select Features", predefined_features)

# Free-text feature
free_feature = st.text_input("Or enter a custom feature")

if free_feature:
    selected_features.append(free_feature)

# Button to generate test cases
if st.button("Generate Test Cases"):
    if not selected_features:
        st.warning("Please select at least one feature.")
    else:
        test_cases = []
        st.info("Generating test cases... This may take a few seconds.")
        for feature in selected_features:
            test_case_text = generate_test_case(feature, standard)
            test_cases.append({
                "Standard": standard,
                "Feature": feature,
                "Test Case": test_case_text
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(test_cases)
        st.success("Test cases generated successfully!")

        # Display test cases
        st.dataframe(df)

        # Buttons to download CSV and Excel
        csv_data = df.to_csv(index=False).encode('utf-8')
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{standard}_test_cases.csv",
            mime="text/csv"
        )
        st.download_button(
            label="Download Excel",
            data=excel_buffer,
            file_name=f"{standard}_test_cases.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
