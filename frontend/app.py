"""
Streamlit frontend for QA Agent.

Provides a user-friendly interface for document upload, knowledge base management,
test case generation, and Selenium script generation.
"""

import streamlit as st
import requests
from typing import Optional, Dict, Any, List
import json


# ==================== Configuration ====================

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="QA Agent - Autonomous Test Generation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== Session State Initialization ====================

if 'test_cases' not in st.session_state:
    st.session_state.test_cases = []
if 'selected_test_case' not in st.session_state:
    st.session_state.selected_test_case = None
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = None
if 'html_content' not in st.session_state:
    st.session_state.html_content = ""


# ==================== Utility Functions ====================

def call_api(endpoint: str, method: str = "GET", data: Optional[Dict] = None, files: Optional[Dict] = None) -> Optional[Dict]:
    """
    Make API call to backend.

    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, DELETE)
        data: JSON data to send
        files: Files to upload

    Returns:
        Optional[Dict]: Response JSON or None on error
    """
    url = f"{API_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, timeout=60)
            else:
                response = requests.post(url, json=data, timeout=60)
        elif method == "DELETE":
            response = requests.delete(url, timeout=30)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        if hasattr(e.response, 'text'):
            st.error(f"Details: {e.response.text}")
        return None


def check_backend_health() -> bool:
    """
    Check if backend API is healthy.

    Returns:
        bool: True if backend is healthy
    """
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_kb_stats() -> Optional[Dict]:
    """Get knowledge base statistics."""
    return call_api("/knowledge-base/stats", method="GET")


def get_uploaded_documents() -> Optional[List[str]]:
    """Get list of uploaded documents."""
    return call_api("/knowledge-base/documents", method="GET")


# ==================== Sidebar ====================

with st.sidebar:
    st.header("⚙️ Configuration")

    # Backend status
    backend_status = check_backend_health()
    if backend_status:
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Disconnected")
        st.info("Make sure the backend is running:\n```\ncd backend\nuvicorn app.main:app --reload\n```")

    st.divider()

    # API URL configuration
    api_url_input = st.text_input(
        "Backend URL",
        value=API_URL,
        help="URL of the FastAPI backend"
    )
    if api_url_input != API_URL:
        API_URL = api_url_input

    st.divider()

    st.markdown("### 📋 Workflow")
    st.markdown("""
    1. **Upload** support documents
    2. **Generate** test cases
    3. **Select** a test case
    4. **Generate** Selenium script
    5. **Download** the script
    """)


# ==================== Main Content ====================

st.title("🤖 Autonomous QA Agent")
st.markdown("Generate test cases and Selenium scripts from documentation")

# Create tabs
tab1, tab2, tab3 = st.tabs([
    "📄 Document Upload",
    "🧪 Test Cases",
    "⚙️ Selenium Scripts"
])


# ==================== Tab 1: Documents ====================

with tab1:
    st.header("📄 Document Management")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Upload Documents")
        st.markdown("Upload product specs, requirements, API docs, validation rules, etc.")

        uploaded_docs = st.file_uploader(
            "Choose files",
            type=["md", "txt", "json", "html", "pdf"],
            accept_multiple_files=True,
            help="Supported formats: MD, TXT, JSON, HTML, PDF"
        )

        if st.button("📤 Upload Documents", disabled=not uploaded_docs):
            if uploaded_docs:
                progress_bar = st.progress(0)
                success_count = 0

                for idx, uploaded_file in enumerate(uploaded_docs):
                    try:
                        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        result = call_api("/knowledge-base/upload", method="POST", files=files)

                        if result:
                            success_count += 1
                            st.success(f"✅ Uploaded: {uploaded_file.name}")

                        progress_bar.progress((idx + 1) / len(uploaded_docs))
                    except Exception as e:
                        st.error(f"❌ Failed to upload {uploaded_file.name}: {str(e)}")

                st.success(f"✅ Successfully uploaded {success_count}/{len(uploaded_docs)} document(s)!")
                st.rerun()

    with col2:
        st.subheader("Knowledge Base Stats")
        kb_stats = get_kb_stats()

        if kb_stats:
            st.metric("Total Chunks", kb_stats.get('total_chunks', 0))
            st.metric("Unique Sources", kb_stats.get('unique_sources', 0))
            st.metric("Total Characters", f"{kb_stats.get('total_characters', 0):,}")
        else:
            st.info("No stats available")

    st.divider()

    st.subheader("Uploaded Documents")
    documents = get_uploaded_documents()

    if documents and len(documents) > 0:
        for doc in documents:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"📄 {doc}")
            with col2:
                if st.button("🗑️", key=f"delete_{doc}"):
                    result = call_api(f"/knowledge-base/documents/{doc}", method="DELETE")
                    if result:
                        st.success(f"Deleted {doc}")
                        st.rerun()
    else:
        st.info("No documents uploaded yet. Upload documents above to get started.")


# ==================== Tab 2: Test Cases ====================

with tab2:
    st.header("🧪 Test Case Generation")

    st.subheader("Generate Test Cases")

    query = st.text_area(
        "What would you like to test?",
        height=100,
        placeholder="Example: Generate test cases for applying discount codes SAVE15, FIRST10, and WELCOME5",
        help="Describe what features or scenarios you want to test"
    )

    col1, col2 = st.columns(2)
    with col1:
        include_negative = st.checkbox("Include negative test cases", value=True)
    with col2:
        max_cases = st.number_input("Max test cases", min_value=1, max_value=50, value=10)

    if st.button("🎯 Generate Test Cases", type="primary", disabled=not query):
        with st.spinner("Generating test cases..."):
            payload = {
                "query": query,
                "include_negative": include_negative,
                "max_test_cases": max_cases,
                "top_k_retrieval": 5
            }

            result = call_api("/test-cases/generate", method="POST", data=payload)

            if result:
                st.session_state.test_cases = result
                st.success(f"✅ Generated {len(result)} test cases!")
                st.rerun()

    st.divider()

    st.subheader("Generated Test Cases")

    if st.session_state.test_cases:
        st.info(f"📊 Total test cases: {len(st.session_state.test_cases)}")

        for idx, tc in enumerate(st.session_state.test_cases):
            with st.expander(f"**{tc['test_id']}**: {tc['test_scenario']}", expanded=idx==0):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Feature:** {tc['feature']}")
                    st.markdown(f"**Type:** {tc['test_type']}")
                    st.markdown(f"**Grounded in:** {tc['grounded_in']}")

                with col2:
                    if st.button("Select for Script", key=f"select_{tc['test_id']}"):
                        st.session_state.selected_test_case = tc
                        st.success(f"Selected {tc['test_id']}")

                st.markdown("**Test Steps:**")
                for step in tc['test_steps']:
                    st.markdown(f"- {step}")

                st.markdown(f"**Expected Result:** {tc['expected_result']}")

                # Download as JSON
                if st.download_button(
                    "💾 Download JSON",
                    data=json.dumps(tc, indent=2),
                    file_name=f"{tc['test_id']}.json",
                    mime="application/json",
                    key=f"download_{tc['test_id']}"
                ):
                    st.success("Downloaded!")

        # Download all test cases
        if st.download_button(
            "💾 Download All Test Cases",
            data=json.dumps(st.session_state.test_cases, indent=2),
            file_name="all_test_cases.json",
            mime="application/json"
        ):
            st.success("Downloaded all test cases!")
    else:
        st.info("No test cases generated yet. Enter a query above and click 'Generate Test Cases'.")


# ==================== Tab 3: Selenium Scripts ====================

with tab3:
    st.header("⚙️ Selenium Script Generation")

    if not st.session_state.selected_test_case:
        st.warning("⚠️ Please select a test case from the 'Test Cases' tab first")
    else:
        tc = st.session_state.selected_test_case
        st.success(f"✅ Selected test case: **{tc['test_id']}** - {tc['test_scenario']}")

        st.divider()

        st.subheader("HTML Content")
        st.markdown("Provide the HTML content for selector extraction")

        # Option to upload HTML file
        uploaded_html = st.file_uploader(
            "Upload HTML file",
            type=["html", "htm"],
            help="HTML file of the web application"
        )

        if uploaded_html:
            st.session_state.html_content = uploaded_html.read().decode('utf-8')
            st.success(f"✅ Loaded HTML from {uploaded_html.name}")

        # Option to paste HTML
        html_paste = st.text_area(
            "Or paste HTML content",
            value=st.session_state.html_content,
            height=200,
            placeholder="<html>...</html>"
        )

        if html_paste:
            st.session_state.html_content = html_paste

        col1, col2 = st.columns(2)
        with col1:
            include_assertions = st.checkbox("Include assertions", value=True)
        with col2:
            include_logging = st.checkbox("Include logging", value=True)

        if st.button("🚀 Generate Selenium Script", type="primary", disabled=not st.session_state.html_content):
            with st.spinner("Generating Selenium script..."):
                payload = {
                    "test_case_id": tc['test_id'],
                    "feature": tc['feature'],
                    "test_scenario": tc['test_scenario'],
                    "test_steps": tc['test_steps'],
                    "expected_result": tc['expected_result'],
                    "grounded_in": tc['grounded_in'],
                    "test_type": tc['test_type'],
                    "html_content": st.session_state.html_content,
                    "include_assertions": include_assertions,
                    "include_logging": include_logging
                }

                result = call_api("/selenium-scripts/generate", method="POST", data=payload)

                if result:
                    st.session_state.generated_script = result
                    st.success("✅ Selenium script generated successfully!")
                    st.rerun()

    st.divider()

    st.subheader("Generated Script")

    if st.session_state.generated_script:
        script_data = st.session_state.generated_script

        # Display script info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", script_data.get('validation_status', 'unknown'))
        with col2:
            st.metric("Selectors Used", len(script_data.get('selectors_used', [])))
        with col3:
            st.metric("Lines of Code", script_data.get('code', '').count('\n') + 1)

        # Display warnings/errors
        if script_data.get('validation_warnings'):
            st.warning("⚠️ Warnings:")
            for warning in script_data['validation_warnings']:
                st.warning(f"- {warning}")

        if script_data.get('validation_errors'):
            st.error("❌ Errors:")
            for error in script_data['validation_errors']:
                st.error(f"- {error}")

        # Display script with syntax highlighting
        st.code(script_data.get('code', ''), language='python')

        # Download button
        if st.download_button(
            "💾 Download Script",
            data=script_data.get('code', ''),
            file_name=f"{script_data.get('test_case_id', 'script')}_selenium.py",
            mime="text/x-python"
        ):
            st.success("Downloaded script!")

        # Display selectors used
        if script_data.get('selectors_used'):
            with st.expander("View Selectors Used"):
                for selector in script_data['selectors_used']:
                    st.code(selector, language='css')
    else:
        st.info("No script generated yet. Select a test case and provide HTML content, then click 'Generate Selenium Script'.")


# ==================== Footer ====================

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>QA Agent v1.0.0 | Autonomous Test Case and Script Generation</p>
</div>
""", unsafe_allow_html=True)
