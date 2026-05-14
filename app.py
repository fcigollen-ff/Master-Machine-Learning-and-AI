import streamlit as st
import google.generativeai as genai

# --- Page Config ---
st.set_page_config(page_title="SQL Whisperer", page_icon="🤖", layout="centered")

# --- Helper Function to Load Style Guide ---
@st.cache_data
def load_style_guide():
    try:
        with open("sql_style_guide.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: Could not find 'sql_style_guide.md'."

style_guide_content = load_style_guide()

# --- Authenticate using Streamlit Secrets ---
# This looks in the server's hidden vault for your key, so users don't have to enter it.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except KeyError:
    st.error("🚨 API Key not found. Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop() # Stops the app from running further if the key is missing

# --- Main UI ---
st.title("🤖 The SQL Whisperer")
st.markdown("Your AI-powered SQL assistant. Refactor messy code to match our style guide, or explain complex queries in plain language.")

tab1, tab2 = st.tabs(["✨ Refactor SQL", "📖 Explain SQL"])

# --- TAB 1: SQL REFACTOR ---
with tab1:
    st.subheader("Format & Refactor Code")
    messy_sql = st.text_area("Input SQL Query:", height=200, key="refactor_input")
    
    if st.button("Refactor Code", type="primary"):
        if not messy_sql:
            st.warning("Please paste some SQL code to refactor.")
        else:
            with st.spinner("Refactoring..."):
                prompt = f"""
                You are a strict Senior Data Engineer. Refactor the following SQL query so it perfectly 
                matches the rules in the provided SQL Style Guide. 
                Return the refactored SQL code inside a code block. Below the code block, provide a brief 
                bulleted list of the specific style guide rules you applied.

                --- SQL STYLE GUIDE ---
                {style_guide_content}

                --- MESSY SQL QUERY ---
                {messy_sql}
                """
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 🎯 Refactored Result")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# --- TAB 2: SQL EXPLAINER ---
with tab2:
    st.subheader("Translate SQL to Plain English/Spanish")
    complex_sql = st.text_area("Input Complex SQL:", height=200, key="explain_input")
    
    if st.button("Explain Code", type="primary"):
        if not complex_sql:
            st.warning("Please paste some SQL code to explain.")
        else:
            with st.spinner("Analyzing code..."):
                prompt = f"""
                You are a helpful database teacher. Explain what the following SQL query is doing in plain, 
                easy-to-understand language. Break it down step-by-step.

                --- SQL QUERY ---
                {complex_sql}
                """
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 🧠 Explanation")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")