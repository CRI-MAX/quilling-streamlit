import streamlit as st
import cv2
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
import os

def load_and_resize_image(uploaded_file, width=400):
    img = Image.open(uploaded_file).convert("RGB")
    img = np.array(img)
    ratio = width / img.shape[1]
    dim = (width, int(img.shape[0] * ratio))
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized

def reduce_colors(img, k=8):
    data = img.reshape((-1, 3))
    data = np.float32(data)
    _, labels, centers = cv2.kmeans(data, k, None,
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
                                    10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    result = centers[labels.flatten()]
    result_img = result.reshape(img.shape)
    return result_img

def detect_edges(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return edges

def save_pdf(edges):
    os.makedirs("output", exist_ok=True)
    temp_path = "output/temp_edges.png"
    cv2.imwrite(temp_path, edges)

    pdf_path = "output/quilling_project.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 800, "Progetto Quilling Generato")
    c.drawImage(temp_path, 100, 400, width=400, height=300)
    c.drawString(100, 380, "Linee guida per strisce di carta")
    c.save()
    return pdf_path

# === INTERFACCIA STREAMLIT ===

st.title("🎨 Generatore Quilling da Immagine")

theme = st.selectbox("🌓 Seleziona tema", ["Chiaro", "Scuro"])
if theme == "Scuro":
    st.markdown(
        """
        <style>
        body { background-color: #1e1e1e; color: white; }
        .stApp { background-color: #1e1e1e; }
        </style>
        """,
        unsafe_allow_html=True
    )

uploaded_file = st.file_uploader("Carica un'immagine (.jpg, .png)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Immagine originale", use_column_width=True)

    width = st.slider("📐 Larghezza immagine (px)", min_value=100, max_value=800, value=400, step=50)
    k = st.slider("🎨 Numero di colori da semplificare", min_value=2, max_value=20, value=8)

    img = load_and_resize_image(uploaded_file, width=width)
    reduced = reduce_colors(img, k=k)
    edges = detect_edges(reduced)

    st.image(edges, caption="Contorni rilevati", use_column_width=True)

    if st.button("Genera PDF Quilling"):
        pdf_path = save_pdf(edges)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Scarica PDF", f, file_name="quilling_project.pdf")