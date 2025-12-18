import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' # Usar CPU para la App
import streamlit as st
import tensorflow as tf
import numpy as np
import pickle
from PIL import Image

st.set_page_config(page_title="Agrosense Pro", page_icon="🌱", layout="centered")

# ==========================================
# 1. CARGA INTELIGENTE DE LA LISTA
# ==========================================
# Intentamos cargar la lista automática que creó Cerebro.py
try:
    with open('nombres_clases.pkl', 'rb') as f:
        class_names = pickle.load(f)
    print(f"✅ Lista cargada del archivo: {len(class_names)} clases.")
except FileNotFoundError:
    # Si no existe (por si acaso), usamos una lista genérica de respaldo
    st.warning("⚠️ Archivo 'nombres_clases.pkl' no encontrado. Usando lista de respaldo.")
    class_names = ['Pepper__bell___Bacterial_spot', 'Pepper__bell___healthy', 
                   'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 
                   'Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight', 
                   'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot', 
                   'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato__Target_Spot', 
                   'Tomato__Tomato_YellowLeaf__Curl_Virus', 'Tomato__Tomato_mosaic_virus', 
                   'Tomato_healthy']

# ==========================================
# 2. DICCIONARIO DE TRADUCCIÓN (Inglés -> Español)
# ==========================================
traducciones = {
    'Tomato___healthy': 'Tomate: Sano y Vigoroso 🍅',
    'Tomato___Bacterial_spot': 'Tomate: Mancha Bacteriana',
    'Tomato___Early_blight': 'Tomate: Tizón Temprano',
    'Tomato___Late_blight': 'Tomate: Tizón Tardío',
    'Tomato___Leaf_Mold': 'Tomate: Moho de la Hoja',
    'Tomato___Septoria_leaf_spot': 'Tomate: Septoriosis',
    'Tomato___Spider_mites Two-spotted_spider_mite': 'Tomate: Araña Roja (Ácaros)',
    'Tomato___Target_Spot': 'Tomate: Mancha Objetivo',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 'Tomate: Virus de la Cuchara',
    'Tomato___Tomato_mosaic_virus': 'Tomate: Virus del Mosaico',
    'Pepper,_bell___healthy': 'Pimiento: Sano 🫑',
    'Pepper,_bell___Bacterial_spot': 'Pimiento: Mancha Bacteriana',
    'Potato___healthy': 'Papa: Sana 🥔',
    'Potato___Early_blight': 'Papa: Tizón Temprano',
    'Potato___Late_blight': 'Papa: Tizón Tardío',
    'Strawberry___healthy': 'Fresa: Sana 🍓',
    'Strawberry___Leaf_scorch': 'Fresa: Quemadura de hoja',
}

# ==========================================
# 3. DICCIONARIO DE RECOMENDACIONES (¡NUEVO!) 💊
# ==========================================
recomendaciones = {
    # --- TOMATES ---
    'Tomato___Bacterial_spot': """
    🔴 **Tratamiento Recomendado:**
    1. **Cobre:** Aplica fungicidas a base de cobre inmediatamente.
    2. **Poda:** Retira las hojas y frutos infectados y quémalos (no compostar).
    3. **Riego:** Evita regar por encima de la planta; riega solo la base para mantener las hojas secas.
    """,
    'Tomato___Early_blight': """
    🟠 **Acciones:**
    1. Mejora la circulación de aire entre plantas (poda de formación).
    2. Aplica fungicidas orgánicos preventivos o químicos (Mancozeb).
    3. Mulching (acolchado) en el suelo ayuda a evitar que las esporas suban.
    """,
    'Tomato___Late_blight': """
    ⚠️ **¡ALERTA GRAVE!**
    1. Esta enfermedad mata rápido. Usa fungicidas sistémicos específicos.
    2. Si la planta está muy afectada, arráncala completa para salvar a las demás.
    3. No plantes papas o tomates en ese mismo sitio el próximo año.
    """,
    'Tomato___Spider_mites Two-spotted_spider_mite': """
    🕷️ **Control de Plaga:**
    1. Aplica Jabón Potásico con Aceite de Neem por las tardes.
    2. Aumenta la humedad (a la araña roja no le gusta el agua).
    3. Si es grave, usa acaricidas específicos (Abamectina).
    """,
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': """
    🦟 **Virus Transmitido por Mosca Blanca:**
    1. No tiene cura química. Debes eliminar la planta infectada.
    2. Coloca trampas cromáticas amarillas para atrapar la mosca blanca.
    3. Usa mallas anti-insectos en el futuro.
    """,
    'Tomato___healthy': "✅ **¡Excelente!** Tu planta está perfecta. Mantén el riego regular y abona cada 15 días.",

    # --- PIMIENTOS ---
    'Pepper,_bell___Bacterial_spot': """
    🔴 **Cuidado:**
    1. Usa semillas certificadas libres de patógenos.
    2. Aplica bactericidas cúpricos.
    3. Elimina restos de cosecha anterior del suelo.
    """,
    'Pepper,_bell___healthy': "✅ **Sano.** Sigue así. Vigila que no le falte calcio para evitar la pudrición apical.",

    # --- PAPAS ---
    'Potato___Late_blight': "⚠️ **Peligro:** Igual que en tomate. Aplica fungicida ya. Revisa si el tubérculo (la papa) está afectado.",
    'Potato___healthy': "✅ **Sana.** Recuerda aporcar (cubrir con tierra) la base para proteger los tubérculos del sol."
}

# ==========================================
# INTERFAZ GRÁFICA
# ==========================================
st.title("🌿 Agrosense Pro")
st.markdown("### 🚑 Diagnóstico y Tratamiento Agrícola")

@st.cache_resource
def load_model():
    return tf.keras.models.load_model('modelo_plantas_samsung.keras')

with st.spinner('Cargando sistema experto...'):
    model = load_model()

file = st.file_uploader("📸 Sube la foto de la hoja enferma", type=["jpg", "png", "jpeg"])

if file is not None:
    image = Image.open(file)
    st.image(image, caption="Muestra subida", width=300)
    
    if st.button("🔍 ANALIZAR Y RECETAR", type="primary"):
        with st.spinner('Consultando base de datos agronómica...'):
            img = image.resize((128, 128))
            img_array = tf.keras.utils.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)

            predictions = model.predict(img_array)
            score = tf.nn.softmax(predictions[0])
            indice = np.argmax(score)
            
            # Protección contra errores de índice
            if indice < len(class_names):
                nombre_ingles = class_names[indice]
                
                # 1. TRADUCCIÓN
                nombre_espanol = traducciones.get(nombre_ingles, nombre_ingles)
                
                # 2. BUSCAR LA RECETA MÉDICA 💊
                # Si no hay receta específica, damos un consejo genérico
                consejo = recomendaciones.get(nombre_ingles, "⚠️ **Consejo General:** Aísla la planta y consulta a un técnico. Mantén buena ventilación.")

                confianza = 100 * np.max(score)

                # MOSTRAR RESULTADOS
                if confianza > 60:
                    st.success(f"### Diagnóstico: {nombre_espanol}")
                    # Mostramos la recomendación en un cuadro azul informativo
                    st.info(consejo)
                else:
                    st.warning(f"### Posible: {nombre_espanol}")
                    st.caption("La IA no está segura. Podría ser otra cosa.")
                
                st.progress(int(confianza))
                st.write(f"Certeza del diagnóstico: **{confianza:.2f}%**")
                
                with st.expander("Ver detalles técnicos (Debug)"):
                    st.text(f"ID Clase: {indice}")
                    st.text(f"Original: {nombre_ingles}")
            else:
                st.error("Error: El modelo predijo una clase fuera de la lista actual.")