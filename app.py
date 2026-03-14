import streamlit as st
import os
import sys
import json
from pathlib import Path

os.chdir("D:\\projet_compression")
sys.path.insert(0, "D:\\projet_compression")

from main import run_pipeline
from process_dataset import process_dataset

# ---- CSS Style Carte ----
st.markdown("""
<style>
    /* Cartes principales */
    .card {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.4);
    }
    .card-title {
        font-size: 1.3em;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 15px;
        border-bottom: 2px solid #4CA1AF;
        padding-bottom: 10px;
    }
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #1a3a4a, #2C3E50) !important;
        color: white !important;
        border: 2px solid #4CA1AF !important;
        border-radius: 25px !important;
        padding: 12px 35px !important;
        font-size: 1.1em !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4CA1AF, #1a3a4a) !important;
        transform: scale(1.02) !important;
    }
    /* Radio buttons */
    div[role="radiogroup"] label {
        background: rgba(26, 58, 74, 0.6) !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        margin: 5px !important;
        color: white !important;
        border: 2px solid #4CA1AF !important;
    }
    /* Texte info (justification) */
    .stAlert p {
        color: #1a3a4a !important;
        font-weight: bold !important;
    }
    /* Titres */
    h1, h2, h3 {
        color: white !important;
    }
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #1a3a4a !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: white !important;
    }
    /* Text input */
    .stTextInput input {
        background: rgba(255,255,255,0.2) !important;
        color: white !important;
        border: 1px solid #4CA1AF !important;
        border-radius: 10px !important;
    }
    /* Success/Error messages */
    .stSuccess {
        background: rgba(0, 128, 0, 0.3) !important;
        border: 1px solid green !important;
        border-radius: 10px !important;
    }
    .stError {
        background: rgba(255, 0, 0, 0.2) !important;
        border: 1px solid red !important;
        border-radius: 10px !important;
    }
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(76, 161, 175, 0.3) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.1) !important;
        border: 2px dashed #4CA1AF !important;
        border-radius: 15px !important;
        padding: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---- Titre ----
st.markdown("""
<div style="text-align:center; padding: 30px 0;">
    <h1 style="color: white; font-size: 2.5em; font-weight: bold;">
        Systeme Intelligent de Compression des Images
    </h1>
    <p style="color: rgba(255,255,255,0.7); font-size: 1.2em;">
        Architecture Multi-Agents + IA Generative (Gemini)
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---- Choix du mode ----
st.markdown('<div class="card"><div class="card-title">Mode de traitement</div>', unsafe_allow_html=True)
mode = st.radio(
    "",
    ["Une seule image", "Dossier complet (dataset)"],
    horizontal=True
)
st.markdown('</div>', unsafe_allow_html=True)

# =============================
# MODE 1 : UNE SEULE IMAGE
# =============================
if mode == "Une seule image":

    st.markdown('<div class="card"><div class="card-title">Charger une image</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Formats supportes : JPG, JPEG, PNG, WEBP, BMP, TIFF",
        type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded:
        st.markdown('<div class="card"><div class="card-title">Apercu de l image</div>', unsafe_allow_html=True)
        st.image(uploaded, caption=uploaded.name, use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Nom du fichier", uploaded.name)
        col2.metric("Taille originale", f"{round(uploaded.size/1024, 2)} KB")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Analyser et Compresser cette image"):
            temp_path = f"D:\\projet_compression\\temp_{uploaded.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded.getbuffer())

            with st.spinner("Pipeline en cours..."):
                report = run_pipeline(temp_path)

            st.markdown('<div class="card"><div class="card-title">Resultats de l analyse</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Type detecte", report["resume"]["type_detecte"])
            c2.metric("Format LLM", report["resume"]["format_recommande_llm"])
            c3.metric("Meilleur format", report["resume"]["meilleur_format_selon_metriques"])
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">Justification de l IA</div>', unsafe_allow_html=True)
            st.info(report["resume"]["justification_llm"])
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">Metriques de qualite</div>', unsafe_allow_html=True)
            for m in report["details"]["evaluation"]["metrics_by_format"]:
                if m.get("metrics"):
                    with st.expander(f"Format : {m['format']}"):
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("PSNR", m["metrics"]["PSNR_dB"])
                        col2.metric("SSIM", m["metrics"]["SSIM"])
                        col3.metric("MSE", m["metrics"]["MSE"])
                        col4.metric("Compression", f"{m['metrics']['compression_ratio_percent']}%")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">Rapport JSON</div>', unsafe_allow_html=True)
            st.code(json.dumps(report, indent=2, ensure_ascii=False), language="json")
            st.markdown('</div>', unsafe_allow_html=True)

            os.remove(temp_path)

# =============================
# MODE 2 : DOSSIER COMPLET
# =============================
else:
    st.markdown('<div class="card"><div class="card-title">Configuration du dataset</div>', unsafe_allow_html=True)
    dataset_path = st.text_input(
        "Chemin vers le dossier dataset",
        value="D:\\projet_compression\\dataset"
    )
    results_path = st.text_input(
        "Chemin vers le dossier results",
        value="D:\\projet_compression\\results"
    )

    if dataset_path and Path(dataset_path).exists():
        all_images = []
        for ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]:
            all_images.extend(list(Path(dataset_path).rglob(f"*{ext}")))
        st.success(f"{len(all_images)} images trouvees dans le dataset !")
        categories = {}
        for img in all_images:
            cat = img.parent.name
            categories[cat] = categories.get(cat, 0) + 1
        cols = st.columns(len(categories))
        for i, (cat, count) in enumerate(categories.items()):
            cols[i].metric(cat, f"{count} images")
    else:
        st.warning("Dossier dataset introuvable !")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Lancer le pipeline sur tout le dataset"):
        if not Path(dataset_path).exists():
            st.error("Dossier dataset introuvable !")
        else:
            with st.spinner("Pipeline en cours sur toutes les images..."):
                summary = process_dataset(dataset_path, results_path)

            st.success(f"Pipeline termine ! {summary['success']}/{summary['total_images']} images traitees.")
            if summary['failed'] > 0:
                st.error(f"Echecs : {summary['failed']}")

            st.markdown('<div class="card"><div class="card-title">Resultats par image</div>', unsafe_allow_html=True)
            for item in summary["items"]:
                if item["status"] == "success":
                    with st.expander(f"OK - {Path(item['image']).name}"):
                        col1, col2 = st.columns(2)
                        col1.write(f"**Meilleur format :** {item['best_format']}")
                        if item.get("report") and Path(item["report"]).exists():
                            with open(item["report"], "r", encoding="utf-8") as f:
                                report = json.load(f)
                            col2.write(f"**Type detecte :** {report['resume']['type_detecte']}")
                            col2.write(f"**Format LLM :** {report['resume']['format_recommande_llm']}")
                            col2.write(f"**Taille originale :** {report['resume']['taille_originale_kb']} KB")
                            st.info(report['resume']['justification_llm'])
                else:
                    with st.expander(f"ERREUR - {Path(item['image']).name}"):
                        st.error(item.get("error", "Erreur inconnue"))
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">Rapport global JSON</div>', unsafe_allow_html=True)
            st.code(json.dumps(summary, indent=2, ensure_ascii=False), language="json")
            st.markdown('</div>', unsafe_allow_html=True)