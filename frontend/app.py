"""
Streamlit frontend for QA Agent.

Provides a user-friendly interface for document upload, knowledge base management,
test case generation, and Selenium script generation.
"""

import streamlit as st
import requests
from typing import Optional, Dict, Any, List


# ==================== Configuration ====================

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="QA Agent - Autonomous Test Generation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
    2. **Upload** HTML file
    3. **Build** knowledge base
    4. **Generate** test cases
    5. **Select** a test case
    6. **Generate** Selenium script
    7. **Download** the script
    """)


# ==================== Main Content ====================

st.title("🤖 Autonomous QA Agent")
st.markdown("Generate test cases and Selenium scripts from documentation")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Documents",
    "🧠 Knowledge Base",
    "🧪 Test Cases",
    "⚙️ Selenium Scripts"
])


# ==================== Tab 1: Documents ====================

with tab1:
    st.header("📄 Document Management")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Upload Support Documents")
        st.markdown("Upload product specs, UI/UX guides, API docs, etc.")

        uploaded_docs = st.file_uploader(
            "Choose files",
            type=["md", "txt", "json", "pdf"],
            accept_multiple_files=True,
            help="Supported formats: MD, TXT, JSON, PDF"
        )

        if st.button("📤 Upload Documents", disabled=not uploaded_docs):
            if uploaded_docs:
                st.info(f"Uploading {len(uploaded_docs)} document(s)...")
                # TODO: Implement upload logic
                st.success("✅ Documents uploaded successfully!")

    with col2:
        st.subheader("Upload HTML File")
        st.markdown("Upload the web page HTML to test")

        uploaded_html = st.file_uploader(
            "Choose HTML file",
            type=["html", "htm"],
            help="HTML file of the web application"
        )

        # Option to paste HTML
        html_paste = st.text_area(
            "Or paste HTML content",
            height=150,
            placeholder="<html>...</html>"
        )

        if st.button("📤 Upload HTML", disabled=not (uploaded_html or html_paste)):
            st.info("Processing HTML...")
            # TODO: Implement HTML upload logic
            st.success("✅ HTML uploaded successfully!")

    st.divider()

    st.subheader("Uploaded Documents")
    # TODO: Display list of uploaded documents
    st.info("No documents uploaded yet")


# ==================== Tab 2: Knowledge Base ====================

with tab2:
    st.header("🧠 Knowledge Base Management")

    st.markdown("""
    The knowledge base is built from your uploaded documents and HTML.
    It creates a searchable index for test case generation.
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Build Knowledge Base")

        chunk_size = st.slider(
            "Chunk Size",
            min_value=500,
            max_value=2000,
            value=1000,
            step=100,
            help="Size of text chunks for processing"
        )

        chunk_overlap = st.slider(
            "Chunk Overlap",
            min_value=0,
            max_value=500,
            value=200,
            step=50,
            help="Overlap between chunks"
        )

        if st.button("🔨 Build Knowledge Base", type="primary"):
            with st.spinner("Building knowledge base..."):
                # TODO: Implement KB build logic
                st.success("✅ Knowledge base built successfully!")

    with col2:
        st.subheader("Status")
        # TODO: Display KB status
        st.metric("Status", "Not Built")
        st.metric("Documents", "0")
        st.metric("Chunks", "0")


# ==================== Tab 3: Test Cases ====================

with tab3:
    st.header("🧪 Test Case Generation")

    st.subheader("Generate Test Cases")

    query = st.text_area(
        "What would you like to test?",
        height=100,
        placeholder="Example: Generate test cases for the discount code feature with both valid and invalid codes",
        help="Describe what features or scenarios you want to test"
    )

    col1, col2 = st.columns(2)
    with col1:
        include_negative = st.checkbox("Include negative test cases", value=True)
    with col2:
        max_cases = st.number_input("Max test cases", min_value=1, max_value=50, value=10)

    if st.button("🎯 Generate Test Cases", type="primary", disabled=not query):
        with st.spinner("Generating test cases..."):
            # TODO: Implement test case generation
            st.success("✅ Generated 5 test cases!")

    st.divider()

    st.subheader("Generated Test Cases")
    # TODO: Display generated test cases
    st.info("No test cases generated yet. Enter a query above and click 'Generate Test Cases'.")


# ==================== Tab 4: Selenium Scripts ====================

with tab4:
    st.header("⚙️ Selenium Script Generation")

    st.markdown("Select a test case to convert into a Selenium WebDriver script")

    # TODO: Test case selection
    st.info("Generate test cases first, then select one to create a Selenium script")

    col1, col2 = st.columns(2)
    with col1:
        include_assertions = st.checkbox("Include assertions", value=True)
    with col2:
        include_logging = st.checkbox("Include logging", value=True)

    if st.button("🚀 Generate Selenium Script", type="primary", disabled=True):
        with st.spinner("Generating Selenium script..."):
            # TODO: Implement script generation
            pass

    st.divider()

    st.subheader("Generated Script")
    # TODO: Display generated script with syntax highlighting
    st.info("No script generated yet")


# ==================== Footer ====================

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>QA Agent v1.0.0 | Autonomous Test Case and Script Generation</p>
</div>
""", unsafe_allow_html=True)
