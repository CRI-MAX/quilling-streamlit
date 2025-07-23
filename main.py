import streamlit as st
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from reportlab.pdfgen import canvas
import os

def load_and_resize_image(uploaded_file, width=400):
    img = Image.open(uploaded_file).convert("RGB")
    ratio = width / img.width
    height = int(img.height * ratio)
    resized = img.resize((width, height))
    return resized

def reduce_colors(img, k=8):
    return img.convert("P", palette=Image.ADAPTIVE, colors=k).convert("RGB")

def detect_edges(img):
    gray = ImageOps.grayscale(img)
    blurred = gray.filter(ImageFilter.GaussianBlur(radius=2))
    edges = blurred.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.invert(edges)  # Inverte: contorni chiari su sfondo scuro
    edges = ImageOps.autocontrast(edges)  # Aumenta il contrasto
    return edges

def save_pdf(edges):
    os.makedirs("output", exist_ok=True)
    temp_path = "output/temp_edges.png"
    edges.convert("RGB").save(temp_path)  # Converti in RGB per compatibilità PDF

    pdf_path = "output/quilling_project.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 800, "Progetto Quilling Generato")
    c.drawImage(temp_path, 100, 400, width=400, height=300)
    c.drawString(100, 380, "Linee guida per strisce di carta")
    c.save()
    return pdf_path

# === INTERFACCIA STREAMLIT ===

st.set_page_config(page_title="Quilling Generator", layout="centered")
st.title("🎨 Generatore Quilling da Immagine")

st.markdown("ℹ️ Puoi cambiare il tema chiaro/scuro cliccando ⚙️ in basso a destra → *Theme*")

uploaded_file = st.file_uploader("Carica un'immagine (.jpg, .png)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Immagine originale", use_container_width=True)

    width = st.slider("📐 Larghezza immagine (px)", min_value=100, max_value=800, value=400, step=50)
    k = st.slider("🎨 Numero di colori da semplificare", min_value=2, max_value=20, value=8)

    img = load_and_resize_image(uploaded_file, width=width)
    reduced = reduce_colors(img, k=k)
    edges = detect_edges(reduced)

    st.image(edges, caption="Contorni rilevati", use_container_width=True)

    if st.button("Genera PDF Quilling"):
        pdf_path = save_pdf(edges)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Scarica PDF", f, file_name="quilling_project.pdf")