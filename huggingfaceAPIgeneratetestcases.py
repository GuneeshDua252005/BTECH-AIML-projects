# # import os
# # import json
# # import re
# # import io
# # import pandas as pd
# # import requests
# # import streamlit as st
# # from typing import Optional
# # from dotenv import load_dotenv

# # # Load .env file if present
# # load_dotenv()
# # "HUGGINGFACE_TOKEN":"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"
# # def get_token_from_sources() -> Optional[str]:
# #     """Look for token in (1) st.secrets, (2) env var, (3) JSON config file."""
    
# #     # 1. Streamlit secrets
# #     try:
# #         if "HUGGINGFACE_TOKEN" in st.secrets:
# #             return st.secrets["HUGGINGFACE_TOKEN"].strip()
# #     except Exception:
# #         pass

# #     # 2. Environment variables
# #     env_val = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
# #     if env_val:
# #         return env_val.strip()

# #     # 3. JSON config
# #     cfg_path = "generatetestcases.json"
# #     if os.path.exists(cfg_path):
# #         try:
# #             with open(cfg_path, "r", encoding="utf-8") as f:
# #                 cfg = json.load(f)
# #             if "HUGGINGFACE_TOKEN" in cfg:
# #                 return cfg["HUGGINGFACE_TOKEN"].strip()
# #         except Exception:
# #             pass

# #     return None


# # def endpoint_exists(model_id: str, token: str = None, timeout: int = 20) -> (bool, str):
# #     """Checks if a Hugging Face model endpoint exists."""
# #     url = f"https://huggingface.co/api/models/{model_id}"
# #     headers = {"Authorization": f"Bearer {token}"} if token else {}

# #     try:
# #         response = requests.get(url, headers=headers, timeout=timeout)
# #         if response.status_code == 200:
# #             return True, f" Model '{model_id}' found."
# #         elif response.status_code == 404:
# #             return False, f" Model '{model_id}' not found on Hugging Face."
# #         else:
# #             return False, f" Error {response.status_code}: {response.text}"
# #     except requests.RequestException as e:
# #         return False, f" Request failed: {str(e)}"

# # def call_hf_inference(model_id: str, prompt: str, token: str, params: Optional[dict] = None, timeout=120):
# #     """POST to HF inference endpoint and return text output."""
# #     api_url = f"https://api-inference.huggingface.co/models/{model_id}"
# #     headers = {"Authorization": f"Bearer {token}"} if token else {}
# #     payload = {"inputs": prompt, "options": {"wait_for_model": True}}
# #     if params:
# #         payload["parameters"] = params

# #     resp = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
# #     if resp.status_code != 200:
# #         try:
# #             err = resp.json()
# #         except Exception:
# #             err = resp.text
# #         raise RuntimeError(f"Hugging Face API error {resp.status_code}: {err}")

# #     data = resp.json()
# #     if isinstance(data, list):
# #         return " ".join([item.get("generated_text", str(item)) for item in data])
# #     elif isinstance(data, dict):
# #         return data.get("generated_text", json.dumps(data))
# #     return str(data)

# # def extract_first_json(text: str):
# #     """Try to extract first JSON object/array from model output."""
# #     m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```", text, re.IGNORECASE)
# #     if m:
# #         try:
# #             return json.loads(m.group(1))
# #         except Exception:
# #             pass
# #     for start in ("{", "["):
# #         i = text.find(start)
# #         if i == -1:
# #             continue
# #         stack = []
# #         pairs = {"{": "}", "[": "]"}
# #         for j in range(i, len(text)):
# #             ch = text[j]
# #             if ch in "{[":
# #                 stack.append(ch)
# #             elif ch in "}]":
# #                 if not stack:
# #                     break
# #                 top = stack[-1]
# #                 if pairs[top] == ch:
# #                     stack.pop()
# #                     if not stack:
# #                         candidate = text[i:j+1]
# #                         try:
# #                             return json.loads(candidate)
# #                         except Exception:
# #                             break
# #                 else:
# #                     break
# #     return None

# # # --------------------
# # # Streamlit UI
# # # --------------------
# # st.set_page_config(page_title="HF: Conformity Test Case Generator", layout="wide")
# # st.title("Hugging Face Conformity Test Case Generator (Streamlit) — Safe Mode")

# # # Sidebar token & model settings
# # auto_token = get_token_from_sources()
# # with st.sidebar.expander("API Key & Model", True):
# #     token = auto_token or st.text_input("Hugging Face token (hf_...)", type="password")
# #     if token:
# #         st.success("Hugging Face token present.")
# #     else:
# #         st.warning("No token found.")

# #     MODEL_NAME = st.text_input("Model name", value="tiiuae/falcon-7b-instruct")
# #     num_cases = st.number_input("Number of test cases", min_value=1, max_value=50, value=5)
# #     max_tokens = st.number_input("Max new tokens", min_value=50, max_value=2000, value=500)
# #     temperature = st.slider("Temperature", 0.0, 1.0, 0.7)

# # protocol = st.text_input("Protocol specification", "SIP (RFC 3261)")
# # feature = st.text_input("Feature to test", "302 Call Redirection")

# # if st.button("Generate Test Cases"):
# #     if not token:
# #         st.error("Hugging Face token required.")
# #         st.stop()

# #     ok, msg = endpoint_exists(MODEL_NAME, token)
# #     if not ok:
# #         st.error(f"Model endpoint check failed: {msg}")
# #         st.stop()
# #     st.info("Model endpoint reachable.")

# #     prompt = f"""
# # Return EXACTLY one valid JSON object (no extra commentary) with a top-level field "test_cases" (an array).
# # Generate {num_cases} test cases for:

# # Protocol: {protocol}
# # Feature: {feature}

# # Each test case object MUST include:
# # - id (string)
# # - title (string)
# # - preconditions (array of strings)
# # - steps (array of strings)
# # - expected_result (string)
# # - type (string): "Manual" or "Automation"
# # - automation_snippet (string, optional)
# # """

# #     params = {"max_new_tokens": max_tokens, "temperature": temperature}
# #     with st.spinner("Requesting Hugging Face model..."):
# #         try:
# #             raw = call_hf_inference(MODEL_NAME, prompt, token, params=params, timeout=120)
# #         except Exception as e:
# #             st.error(f"API request failed: {e}")
# #             st.stop()

# #     with st.expander("Raw model output"):
# #         st.code(raw)

# #     parsed = extract_first_json(raw)
# #     if parsed is None:
# #         st.error("Could not extract valid JSON from model output.")
# #         st.stop()

# #     if not isinstance(parsed, dict) or "test_cases" not in parsed:
# #         st.error("Parsed JSON does not contain 'test_cases'.")
# #         st.json(parsed)
# #         st.stop()

# #     df = pd.DataFrame([
# #         {
# #             "id": tc.get("id", ""),
# #             "title": tc.get("title", ""),
# #             "preconditions": " ; ".join(tc.get("preconditions", [])),
# #             "steps": " | ".join(tc.get("steps", [])),
# #             "expected_result": tc.get("expected_result", ""),
# #             "type": tc.get("type", ""),
# #             "automation_snippet": tc.get("automation_snippet", "")
# #         }
# #         for tc in parsed["test_cases"]
# #     ])

# #     st.success(f"Generated {len(df)} test cases.")
# #     st.dataframe(df, use_container_width=True)

# #     csv_bytes = df.to_csv(index=False).encode("utf-8")
# #     st.download_button("Download CSV", csv_bytes, "test_cases.csv", "text/csv")

# #     towrite = io.BytesIO()
# #     with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
# #         df.to_excel(writer, index=False, sheet_name="TestCases")
# #     towrite.seek(0)
# #     st.download_button("Download Excel", towrite.getvalue(), "test_cases.xlsx",
# #                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# #     json_bytes = json.dumps(parsed, indent=2).encode("utf-8")
# #     st.download_button("Download JSON", json_bytes, "test_cases.json", "application/json")

# import os
# import json
# import re
# import io
# import pandas as pd
# import requests
# import streamlit as st
# from typing import Optional
# from dotenv import load_dotenv

# # --------------------
# # Load Environment Variables
# # --------------------
# load_dotenv()  # Reads from .env file if present

# # --------------------
# # Helper: Get Token
# # --------------------
# def get_token_from_sources() -> Optional[str]:
#     """Look for token in (1) st.secrets, (2) env var, (3) JSON config file."""
    
#     # 1. Streamlit secrets
#     try:
#         if "HUGGINGFACE_TOKEN" in st.secrets:
#             return st.secrets["HUGGINGFACE_TOKEN"].strip()
#     except Exception:
#         pass

#     # 2. Environment variables
#     env_val = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
#     if env_val:
#         return env_val.strip()

#     # 3. JSON config
#     cfg_path = "generatetestcases.json"
#     if os.path.exists(cfg_path):
#         try:
#             with open(cfg_path, "r", encoding="utf-8") as f:
#                 cfg = json.load(f)
#             if "HUGGINGFACE_TOKEN" in cfg:
#                 return cfg["HUGGINGFACE_TOKEN"].strip()
#         except Exception:
#             pass

#     return None

# # --------------------
# # Helper: Check Model Endpoint
# # --------------------
# def endpoint_exists(model_id: str, token: str = None, timeout: int = 20) -> (bool, str):
#     """Checks if a Hugging Face model endpoint exists."""
#     url = f"https://huggingface.co/api/models/{model_id}"
#     headers = {"Authorization": f"Bearer {token}"} if token else {}

#     try:
#         response = requests.get(url, headers=headers, timeout=timeout)
#         if response.status_code == 200:
#             return True, f"Model '{model_id}' found."
#         elif response.status_code == 404:
#             return False, f"Model '{model_id}' not found on Hugging Face."
#         else:
#             return False, f"Error {response.status_code}: {response.text}"
#     except requests.RequestException as e:
#         return False, f"Request failed: {str(e)}"

# # --------------------
# # Helper: Call HF Inference API
# # --------------------
# def call_hf_inference(model_id: str, prompt: str, token: str, params: Optional[dict] = None, timeout=120):
#     """POST to HF inference endpoint and return text output."""
#     api_url = f"https://api-inference.huggingface.co/models/{model_id}"
#     headers = {"Authorization": f"Bearer {token}"} if token else {}
#     payload = {"inputs": prompt, "options": {"wait_for_model": True}}
#     if params:
#         payload["parameters"] = params

#     resp = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
#     if resp.status_code != 200:
#         try:
#             err = resp.json()
#         except Exception:
#             err = resp.text
#         raise RuntimeError(f"Hugging Face API error {resp.status_code}: {err}")

#     data = resp.json()
#     if isinstance(data, list):
#         return " ".join([item.get("generated_text", str(item)) for item in data])
#     elif isinstance(data, dict):
#         return data.get("generated_text", json.dumps(data))
#     return str(data)

# # --------------------
# # Helper: Extract First JSON
# # --------------------
# def extract_first_json(text: str):
#     """Try to extract first JSON object/array from model output."""
#     m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```", text, re.IGNORECASE)
#     if m:
#         try:
#             return json.loads(m.group(1))
#         except Exception:
#             pass
#     for start in ("{", "["):
#         i = text.find(start)
#         if i == -1:
#             continue
#         stack = []
#         pairs = {"{": "}", "[": "]"}
#         for j in range(i, len(text)):
#             ch = text[j]
#             if ch in "{[":
#                 stack.append(ch)
#             elif ch in "}]":
#                 if not stack:
#                     break
#                 top = stack[-1]
#                 if pairs[top] == ch:
#                     stack.pop()
#                     if not stack:
#                         candidate = text[i:j+1]
#                         try:
#                             return json.loads(candidate)
#                         except Exception:
#                             break
#                 else:
#                     break
#     return None

# # --------------------
# # Streamlit UI
# # --------------------
# st.set_page_config(page_title="HF: Conformity Test Case Generator", layout="wide")
# st.title("Hugging Face Conformity Test Case Generator (Streamlit) — Safe Mode")

# # Sidebar token & model settings
# auto_token = get_token_from_sources()
# with st.sidebar.expander("API Key & Model", True):
#     token = auto_token or st.text_input("Hugging Face token (hf_...)", type="password")
#     if token:
#         st.success("Hugging Face token present.")
#     else:
#         st.warning("No token found.")

#     MODEL_NAME = st.text_input("Model name", value="tiiuae/falcon-7b-instruct")
#     num_cases = st.number_input("Number of test cases", min_value=1, max_value=50, value=5)
#     max_tokens = st.number_input("Max new tokens", min_value=50, max_value=2000, value=500)
#     temperature = st.slider("Temperature", 0.0, 1.0, 0.7)

# protocol = st.text_input("Protocol specification", "SIP (RFC 3261)")
# feature = st.text_input("Feature to test", "302 Call Redirection")

# if st.button("Generate Test Cases"):
#     if not token:
#         st.error("Hugging Face token required.")
#         st.stop()

#     ok, msg = endpoint_exists(MODEL_NAME, token)
#     if not ok:
#         st.error(f"Model endpoint check failed: {msg}")
#         st.stop()
#     st.info("Model endpoint reachable.")

#     prompt = f"""
# Return EXACTLY one valid JSON object (no extra commentary) with a top-level field "test_cases" (an array).
# Generate {num_cases} test cases for:

# Protocol: {protocol}
# Feature: {feature}

# Each test case object MUST include:
# - id (string)
# - title (string)
# - preconditions (array of strings)
# - steps (array of strings)
# - expected_result (string)
# - type (string): "Manual" or "Automation"
# - automation_snippet (string, optional)
# """

#     params = {"max_new_tokens": max_tokens, "temperature": temperature}
#     with st.spinner("Requesting Hugging Face model..."):
#         try:
#             raw = call_hf_inference(MODEL_NAME, prompt, token, params=params, timeout=120)
#         except Exception as e:
#             st.error(f"API request failed: {e}")
#             st.stop()

#     with st.expander("Raw model output"):
#         st.code(raw)

#     parsed = extract_first_json(raw)
#     if parsed is None:
#         st.error("Could not extract valid JSON from model output.")
#         st.stop()

#     if not isinstance(parsed, dict) or "test_cases" not in parsed:
#         st.error("Parsed JSON does not contain 'test_cases'.")
#         st.json(parsed)
#         st.stop()

#     df = pd.DataFrame([
#         {
#             "id": tc.get("id", ""),
#             "title": tc.get("title", ""),
#             "preconditions": " ; ".join(tc.get("preconditions", [])),
#             "steps": " | ".join(tc.get("steps", [])),
#             "expected_result": tc.get("expected_result", ""),
#             "type": tc.get("type", ""),
#             "automation_snippet": tc.get("automation_snippet", "")
#         }
#         for tc in parsed["test_cases"]
#     ])

#     st.success(f"Generated {len(df)} test cases.")
#     st.dataframe(df, use_container_width=True)

#     # CSV Download
#     csv_bytes = df.to_csv(index=False).encode("utf-8")
#     st.download_button("Download CSV", csv_bytes, "test_cases.csv", "text/csv")

#     # Excel Download
#     towrite = io.BytesIO()
#     with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
#         df.to_excel(writer, index=False, sheet_name="TestCases")
#     towrite.seek(0)
#     st.download_button(
#         "Download Excel",
#         towrite.getvalue(),
#         "test_cases.xlsx",
#         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

#     # JSON Download
#     json_bytes = json.dumps(parsed, indent=2).encode("utf-8")
#     st.download_button("Download JSON", json_bytes, "test_cases.json", "application/json")
import os
import json
import re
import io
import pandas as pd
import requests
import streamlit as st
from typing import Optional
from dotenv import load_dotenv

# --------------------
# Load Environment Variables
# --------------------
load_dotenv()  # Reads from .env file if present

# --------------------
# Helper: Get Token
# --------------------
def get_token_from_sources() -> Optional[str]:
    """Look for token in (1) st.secrets, (2) env var, (3) JSON config file."""
    try:
        if "HUGGINGFACE_TOKEN" in st.secrets:
            return st.secrets["HUGGINGFACE_TOKEN"].strip()
    except Exception:
        pass
    env_val = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
    if env_val:
        return env_val.strip()
    cfg_path = "generatetestcases.json"
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if "HUGGINGFACE_TOKEN" in cfg:
                return cfg["HUGGINGFACE_TOKEN"].strip()
        except Exception:
            pass
    return None

# --------------------
# Helper: Check Model Endpoint
# --------------------
def endpoint_exists(model_id: str, token: str = None, timeout: int = 20) -> (bool, str):
    """Checks if a Hugging Face model endpoint exists."""
    url = f"https://huggingface.co/api/models/{model_id}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return True, f"Model '{model_id}' found."
        elif response.status_code == 404:
            return False, f"Model '{model_id}' not found on Hugging Face."
        else:
            return False, f"Error {response.status_code}: {response.text}"
    except requests.RequestException as e:
        return False, f"Request failed: {str(e)}"

# --------------------
# Helper: Call HF Inference API
# --------------------
def call_hf_inference(model_id: str, prompt: str, token: str, params: Optional[dict] = None, timeout=120):
    """POST to HF inference endpoint and return text output."""
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    if params:
        payload["parameters"] = params
    resp = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code != 200:
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        raise RuntimeError(f"Hugging Face API error {resp.status_code}: {err}")
    data = resp.json()
    if isinstance(data, list):
        return " ".join([item.get("generated_text", str(item)) for item in data])
    elif isinstance(data, dict):
        return data.get("generated_text", json.dumps(data))
    return str(data)

# --------------------
# Helper: Extract First JSON
# --------------------
def extract_first_json(text: str):
    """Try to extract first JSON object/array from model output."""
    m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```", text, re.IGNORECASE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    for start in ("{", "["):
        i = text.find(start)
        if i == -1:
            continue
        stack = []
        pairs = {"{": "}", "[": "]"}
        for j in range(i, len(text)):
            ch = text[j]
            if ch in "{[":
                stack.append(ch)
            elif ch in "}]":
                if not stack:
                    break
                top = stack[-1]
                if pairs[top] == ch:
                    stack.pop()
                    if not stack:
                        candidate = text[i:j+1]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            break
                else:
                    break
    return None

# --------------------
# Streamlit UI
# --------------------
st.set_page_config(page_title="HF: Conformity Test Case Generator", layout="wide")
st.title("Hugging Face Conformity Test Case Generator (Streamlit) — Safe Mode")

auto_token = get_token_from_sources()
with st.sidebar.expander("API Key & Model", True):
    token = auto_token or st.text_input("Hugging Face token (hf_...)", type="password")
    if token:
        st.success("Hugging Face token present.")
    else:
        st.warning("No token found.")
    MODEL_NAME = st.text_input("Model name", value="tiiuae/falcon-7b-instruct")
    num_cases = st.number_input("Number of test cases", min_value=1, max_value=50, value=5)
    max_tokens = st.number_input("Max new tokens", min_value=50, max_value=2000, value=500)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)

protocol = st.text_input("Protocol specification", "SIP (RFC 3261)")
feature = st.text_input("Feature to test", "302 Call Redirection")

if st.button("Generate Test Cases"):
    if not token:
        st.error("Hugging Face token required.")
        st.stop()

    ok, msg = endpoint_exists(MODEL_NAME, token)
    if not ok:
        st.warning(f"{msg} — switching to fallback model: mistralai/Mistral-7B-Instruct-v0.2")
        MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
        ok, msg = endpoint_exists(MODEL_NAME, token)
        if not ok:
            st.error(f"Fallback model also failed: {msg}")
            st.stop()

    st.info(f"Using model: {MODEL_NAME}")

    prompt = f"""
Return EXACTLY one valid JSON object (no extra commentary) with a top-level field "test_cases" (an array).
Generate {num_cases} test cases for:

Protocol: {protocol}
Feature: {feature}

Each test case object MUST include:
- id (string)
- title (string)
- preconditions (array of strings)
- steps (array of strings)
- expected_result (string)
- type (string): "Manual" or "Automation"
- automation_snippet (string, optional)
"""

    params = {"max_new_tokens": max_tokens, "temperature": temperature}
    with st.spinner("Requesting Hugging Face model..."):
        try:
            raw = call_hf_inference(MODEL_NAME, prompt, token, params=params, timeout=120)
        except Exception as e:
            st.error(f"API request failed: {e}")
            st.stop()

    with st.expander("Raw model output"):
        st.code(raw)

    parsed = extract_first_json(raw)
    if parsed is None:
        st.error("Could not extract valid JSON from model output.")
        st.stop()

    if not isinstance(parsed, dict) or "test_cases" not in parsed:
        st.error("Parsed JSON does not contain 'test_cases'.")
        st.json(parsed)
        st.stop()

    df = pd.DataFrame([
        {
            "id": tc.get("id", ""),
            "title": tc.get("title", ""),
            "preconditions": " ; ".join(tc.get("preconditions", [])),
            "steps": " | ".join(tc.get("steps", [])),
            "expected_result": tc.get("expected_result", ""),
            "type": tc.get("type", ""),
            "automation_snippet": tc.get("automation_snippet", "")
        }
        for tc in parsed["test_cases"]
    ])

    st.success(f"Generated {len(df)} test cases.")
    st.dataframe(df, use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv_bytes, "test_cases.csv", "text/csv")

    towrite = io.BytesIO()
    with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="TestCases")
    towrite.seek(0)
    st.download_button(
        "Download Excel",
        towrite.getvalue(),
        "test_cases.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    json_bytes = json.dumps(parsed, indent=2).encode("utf-8")
    st.download_button("Download JSON", json_bytes, "test_cases.json", "application/json")

