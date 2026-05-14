import streamlit as st
import google.generativeai as genai

# --- Configuración de la página ---
st.set_page_config(page_title="Asistente SQL con IA", page_icon="🤖", layout="centered")

# --- Función auxiliar para cargar la guía de estilo ---
@st.cache_data
def load_style_guide():
    try:
        with open("sql_style_guide.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: No se pudo encontrar el archivo 'sql_style_guide.md'."

style_guide_content = load_style_guide()

# --- Autenticación usando los Secretos de Streamlit ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except KeyError:
    st.error("🚨 No se encontró la API Key. Por favor, añade GEMINI_API_KEY a los secretos de Streamlit.")
    st.stop()

# --- Interfaz Principal (UI) ---
st.title("🤖 Asistente SQL con IA")
st.markdown("Tu asistente de SQL impulsado por Inteligencia Artificial. Refactoriza código desordenado para que coincida con nuestra guía de estilo, o explica consultas complejas en lenguaje claro.")

tab1, tab2 = st.tabs(["✨ Refactorizar SQL", "📖 Explicar SQL"])

# --- PESTAÑA 1: REFACTORIZACIÓN DE SQL ---
with tab1:
    st.subheader("Formatear y Refactorizar Código")
    messy_sql = st.text_area("Introduce la consulta SQL:", height=200, key="refactor_input")
    
    if st.button("Refactorizar Código", type="primary"):
        if not messy_sql:
            st.warning("Por favor, pega un poco de código SQL para refactorizar.")
        else:
            with st.spinner("Refactorizando..."):
                prompt = f"""
                Eres un Ingeniero de Datos Senior estricto. Refactoriza la siguiente consulta SQL para que 
                coincida perfectamente con las reglas de la Guía de Estilo SQL proporcionada. 
                Devuelve el código SQL refactorizado dentro de un bloque de código. Debajo del bloque de código, 
                proporciona una breve lista de viñetas EN ESPAÑOL de las reglas específicas de la guía de estilo que aplicaste.

                --- GUÍA DE ESTILO SQL ---
                {style_guide_content}

                --- CONSULTA SQL DESORDENADA ---
                {messy_sql}
                """
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 🎯 Resultado Refactorizado")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Ocurrió un error: {e}")

# --- PESTAÑA 2: EXPLICACIÓN DE SQL ---
with tab2:
    st.subheader("Traducir SQL a Lenguaje Natural")
    complex_sql = st.text_area("Introduce el SQL complejo:", height=200, key="explain_input")
    
    if st.button("Explicar Código", type="primary"):
        if not complex_sql:
            st.warning("Por favor, pega un poco de código SQL para explicar.")
        else:
            with st.spinner("Analizando el código..."):
                prompt = f"""
                Eres un profesor de bases de datos muy útil. Explica qué está haciendo la siguiente consulta SQL 
                en un lenguaje claro, fácil de entender y EN ESPAÑOL. Desglósalo paso a paso.

                --- CONSULTA SQL ---
                {complex_sql}
                """
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 🧠 Explicación")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Ocurrió un error: {e}")
