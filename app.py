import streamlit as st
import google.generativeai as genai
import PyPDF2
import io

# --- Page Config ---
st.set_page_config(
    page_title="AI Quote Comparison",
    page_icon="📄",
    layout="wide"
)

# --- Header ---
st.title("📄 AI Quote Comparison & Document Extraction")
st.caption("Upload your quote documents and let AI compare them instantly.")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Paste your key here..."
    )
    st.markdown("[🔑 Get a free Gemini API key →](https://aistudio.google.com)")
    st.divider()
    st.markdown("**How to use:**")
    st.markdown("1. Paste your Gemini API key above")
    st.markdown("2. Upload your quote files (PDF or TXT)")
    st.markdown("3. Choose what to focus on")
    st.markdown("4. Click **Compare Quotes**")

# --- Text Extraction Helper ---
def extract_text(file) -> str:
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()
    else:
        return file.read().decode("utf-8").strip()

# --- Step 1: Upload Files ---
st.subheader("Step 1 — Upload Your Quote Documents")
uploaded_files = st.file_uploader(
    "Accepts PDF or TXT files. You can upload multiple at once.",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

# --- Step 2: Preview Extracted Text ---
extracted = {}

if uploaded_files:
    st.subheader("Step 2 — Extracted Content Preview")
    cols = st.columns(len(uploaded_files))
    for i, f in enumerate(uploaded_files):
        text = extract_text(f)
        extracted[f.name] = text
        with cols[i]:
            with st.expander(f"📃 {f.name}", expanded=True):
                st.text_area(
                    "Extracted text",
                    text if text else "⚠️ No text found in this file.",
                    height=200,
                    key=f"preview_{f.name}",
                    label_visibility="collapsed"
                )

# --- Step 3: AI Comparison ---
if extracted:
    st.subheader("Step 3 — AI Comparison")

    focus = st.multiselect(
        "What should the AI focus on when comparing?",
        ["Price", "Delivery time", "Warranty", "Payment terms",
         "Scope of work", "Terms & conditions", "Overall recommendation"],
        default=["Price", "Delivery time", "Overall recommendation"]
    )

    extra_instructions = st.text_input(
        "Any extra instructions for the AI? (optional)",
        placeholder="e.g. We prefer local suppliers, budget is under ₱50,000"
    )

    compare_btn = st.button("🔍 Compare Quotes with AI", type="primary", use_container_width=True)

    if compare_btn:
        if not api_key:
            st.error("⚠️ Please enter your Gemini API key in the sidebar first.")
        elif not focus:
            st.warning("Please select at least one focus area.")
        else:
            with st.spinner("AI is analyzing your documents..."):
                try:
                    docs_text = "\n\n---\n\n".join(
                        f"DOCUMENT: {name}\n{text}"
                        for name, text in extracted.items()
                    )
                    focus_str = ", ".join(focus)
                    extra = f"\nExtra instructions: {extra_instructions}" if extra_instructions else ""

                    prompt = f"""You are an expert procurement analyst.
Compare the following quote documents carefully. Focus on: {focus_str}.{extra}

{docs_text}

Please provide:
1. A clear summary table comparing key details across all quotes
2. Pros and cons of each quote
3. A final recommendation with clear reasoning

Be concise, practical, and use markdown formatting."""

                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(prompt)

                    st.divider()
                    st.markdown("### 🤖 AI Analysis Result")
                    st.markdown(response.text)

                    st.download_button(
                        label="⬇️ Download Analysis as TXT",
                        data=response.text,
                        file_name="quote_analysis.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")
                    st.info("Double-check your API key and make sure your files contain readable text.")

elif not uploaded_files:
    st.info("⬆️ Upload at least one quote document above to get started.")
