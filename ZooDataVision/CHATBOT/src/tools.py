import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.tools import tool
try:
    from data_loader import retrieve_info
except ImportError:
    from src.data_loader import retrieve_info

@tool
def search_zoodatavision_data(query: str) -> str:
    """
    Útil para encontrar información sobre detecciones de cámaras trampa del proyecto ZooDataVision.
    Permite consultar:
    - Clases de animales detectados (mamíferos, aves, etc.).
    - Niveles de confianza de las predicciones.
    - Estadísticas generales (promedios, conteos, máximos y mínimos).
    - Detalles sobre archivos de imágenes específicos.
    
    Args:
        query (str): La pregunta o término de búsqueda del usuario (ej: "¿Cuántos mamíferos medianos hay?", "Promedio de confianza").
    """
    return retrieve_info(query)

tools = [search_zoodatavision_data]

if __name__ == "__main__":
    print("🦁 Probando Tool de ZooDataVision...")
    
    # 1. Seleccionamos la herramienta
    tool = tools[0]
    print(f"Nombre: {tool.name}")
    print(f"Descripción: {tool.description}")
    
    # 2. Simulamos una consulta del chatbot
    preguntas_test = [
        "¿Cuál es el promedio de confianza general?",
        "¿Cuántos animales de cada categoría encontraste?"
    ]
    
    for p in preguntas_test:
        print(f"\n🧪 Probando input: '{p}'")
        try:
            resultado = tool.invoke(p)
            print(f"Resultado:\n{resultado[:200]}...") 
        except Exception as e:
            print(f"Error: {e}")