import streamlit as st
import sys
import os

# --- CONFIGURACIÓN DE RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from src.graph import app as graph_app
except ImportError:
    try:
        from CHATBOT.src.graph import app as graph_app
    except ImportError:
        graph_app = None

def render_chatbot():
    """
    Renderiza el chatbot con historial persistente, 
    pregunta inmediata y entrada fija al final.
    """
    
    st.markdown("""
        <style>
        .stChatMessage { border-radius: 15px; padding: 10px; border: 1px solid #e0e0e0; }
        h1 { background: -webkit-linear-gradient(45deg, #2e7d32, #81c784);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        </style>
        """, unsafe_allow_html=True)

    st.header("🦁 ZooDataVision Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "¡Hola! Soy tu analista de biodiversidad. ¿Qué deseas consultar hoy?"}
        ]

    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Escribe aquí tu pregunta sobre el dataset..."):
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("🔍 Consultando RAG y analizando datos..."):
                    if graph_app is None:
                        response_content = "❌ Error: El motor del chatbot (Grafo) no está disponible."
                    else:
                        try:
                            # Invocación al Grafo de LangGraph
                            result = graph_app.invoke({"question": prompt})
                            
                            answer = result.get("answer", "No pude generar una respuesta.")
                            category = result.get("category", "CHAT")
                            context = result.get("context", "")

                            response_content = answer
                            
                            # Si es búsqueda, añadimos la evidencia del CSV
                            if category == "SEARCH" and context:
                                response_content += f"\n\n---\n**📊 Evidencia (Datos CSV):**\n```\n{context[:600]}...\n```"
                        
                        except Exception as e:
                            response_content = f"❌ Error en el procesamiento: {e}"

                    st.markdown(response_content)
        
        st.session_state.messages.append({"role": "assistant", "content": response_content})
        

        st.rerun()

# Bloque de ejecución
if __name__ == "__main__":
    st.set_page_config(page_title="ZooDataVision AI", page_icon="🦁", layout="centered")
    render_chatbot()