import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# ---------------- INTERFAZ STREAMLIT ----------------

st.set_page_config(page_title='Tablero Inteligente')
st.title('🧠 Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("Esta aplicación demuestra la capacidad de una IA para **interpretar un boceto dibujado** directamente en el navegador.")
    st.subheader("Propiedades del Tablero")

    # Dimensiones del tablero
    st.subheader("Dimensiones del tablero")
    canvas_width = st.slider("Ancho del tablero", 300, 700, 500, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    # Herramienta de dibujo
    drawing_mode = st.selectbox(
        "Herramienta de Dibujo:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )

    # Ancho del trazo
    stroke_width = st.slider("Selecciona el ancho de línea", 1, 30, 5)

    # Color del trazo
    stroke_color = st.color_picker("Color del trazo", "#000000")

    # Color de fondo
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")

st.subheader("Dibuja tu boceto en el panel y presiona el botón para analizarlo 👇")

# Crear el canvas dinámico
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode=drawing_mode,
    key=f"canvas_{canvas_width}_{canvas_height}",
)

# ---------------- API OPENAI ----------------
ke = st.text_input('🔑 Ingresa tu Clave API de OpenAI')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

analyze_button = st.button("🔍 Analizar Imagen", type="secondary")

# ---------------- PROCESAMIENTO ----------------
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("Analizando tu dibujo con inteligencia artificial..."):
        # Convertir canvas a imagen
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('img.png')
        
        # Codificar la imagen en base64
        base64_image = encode_image_to_base64("img.png")
        prompt_text = "Describe brevemente en español la imagen que te muestro."

        try:
            full_response = ""
            message_placeholder = st.empty()

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content

        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")

else:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API key antes de analizar.")
