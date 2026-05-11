import streamlit as st
import anthropic
import PyPDF2
import io

# --- Page Config ---
st.set_page_config(page_title="AI Quote Comparison", page_icon="📄", layout="wide")
st.title("📄 AI Quote Comparison & Document Extraction")
st.caption("Upload quote documents and let AI compare them for you.")

# --- Sidebar: API Key ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Anthropic API Key", type="password")
    st.markdown("[Get your API key →](https://console.anthropic.com/)")

# --- File Upload ---
st.subheader("1. Upload Your Quote Documents")
uploaded_files = st.file_uploader(
    "Upload PDF or TXT quote files",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

# --- Extract Text Helper ---
def extract_text(file) -> str:
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        return file.read().decode("utf-8")

# --- Show Extracted Text ---
extracted = {}
if uploaded_files:
    st.subheader("2. Extracted Content")
    for f in uploaded_files:
        text = extract_text(f)
        extracted[f.name] = text
        with st.expander(f"📃 {f.name}"):
            st.text_area("Content", text, height=200, key=f.name)

# --- AI Comparison ---
if extracted and api_key:
    st.subheader("3. AI Comparison")
    
    focus = st.multiselect(
        "What should the AI focus on?",
        ["Price", "Delivery time", "Warranty", "Terms & conditions", "Overall recommendation"],
        default=["Price", "Overall recommendation"]
    )

    if st.button("🔍 Compare Quotes with AI", type="primary"):
        with st.spinner("Analyzing documents..."):
            docs_text = "\n\n---\n\n".join(
                f"DOCUMENT: {name}\n{text}" for name, text in extracted.items()
            )
            focus_str = ", ".join(focus)

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": f"""You are an expert procurement analyst. Compare the following quote documents.
Focus on: {focus_str}

{docs_text}

Provide:
1. A summary table comparing key details
2. Pros and cons of each quote
3. A clear recommendation with reasoning"""
                }]
            )

            st.markdown("### 🤖 AI Analysis")
            st.markdown(response.content[0].text)

elif extracted and not api_key:
    st.warning("⚠️ Add your Anthropic API key in the sidebar to enable AI comparison.")
