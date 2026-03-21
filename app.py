import streamlit as st
import os, sys, json
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd

os.chdir("D:\\projet_compression")
sys.path.insert(0, "D:\\projet_compression")

from main import run_pipeline
from process_dataset import process_dataset

st.markdown("""
<style>
.card {background: rgba(255,255,255,0.15); border-radius: 15px; padding: 25px; margin: 15px 0; border: 1px solid rgba(255,255,255,0.4);}
.card-title {font-size: 1.3em; font-weight: bold; color: #ffffff; margin-bottom: 15px; border-bottom: 2px solid #4CA1AF; padding-bottom: 10px;}
.stButton > button {background: linear-gradient(135deg, #1a3a4a, #2C3E50) !important; color: white !important; border: 2px solid #4CA1AF !important; border-radius: 25px !important; padding: 12px 35px !important; font-size: 1.1em !important; width: 100% !important;}
.stButton > button:hover {background: linear-gradient(135deg, #4CA1AF, #1a3a4a) !important;}
div[role="radiogroup"] label {background: rgba(26,58,74,0.6) !important; border-radius: 10px !important; padding: 8px 20px !important; margin: 5px !important; color: white !important; border: 2px solid #4CA1AF !important;}
.stAlert p {color: #1a3a4a !important; font-weight: bold !important;}
h1, h2, h3 {color: white !important;}
p {color: white !important;}
label {color: white !important;}
.stTextInput label {color: white !important;}
.stTextInput input {background: rgba(255,255,255,0.2) !important; color: white !important; border: 1px solid #4CA1AF !important; border-radius: 10px !important;}
[data-testid="stMetricValue"] {color: #1a3a4a !important; font-weight: bold !important;}
[data-testid="stMetricLabel"] {color: white !important;}
.stSuccess {background: rgba(0,128,0,0.3) !important; border: 1px solid green !important; border-radius: 10px !important;}
.stError {background: rgba(255,0,0,0.2) !important; border: 1px solid red !important; border-radius: 10px !important;}
.streamlit-expanderHeader {background: rgba(76,161,175,0.3) !important; border-radius: 10px !important; color: white !important;}
[data-testid="stFileUploader"] {background: rgba(255,255,255,0.1) !important; border: 2px dashed #4CA1AF !important; border-radius: 15px !important; padding: 10px !important;}
.stDataFrame {color: #1a3a4a !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 30px 0;">
<h1 style="color: white; font-size: 2.5em; font-weight: bold;">Systeme Intelligent de Compression des Images</h1>
<p style="color: rgba(255,255,255,0.7); font-size: 1.2em;">Architecture Multi-Agents + IA Generative (Gemini)</p>
</div>
""", unsafe_allow_html=True)

st.divider()

COLORS = ["#4CA1AF", "#2C3E50", "#27AE60", "#E74C3C", "#F39C12"]

def graphiques_image(report):
    metrics = report["details"]["evaluation"]["metrics_by_format"]
    formats = [m["format"] for m in metrics]
    tailles = [m["compressed_size_kb"] for m in metrics]
    psnr = []
    ssim = []
    for m in metrics:
        p = m["metrics"]["PSNR_dB"]
        psnr.append(100 if p == "Infini" else float(p))
        ssim.append(float(m["metrics"]["SSIM"]))
    st.markdown('<div class="card"><div class="card-title">Graphiques de comparaison</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fig1 = go.Figure(go.Bar(x=formats, y=tailles, marker_color=COLORS, text=[f"{t:.1f} KB" for t in tailles], textposition="auto"))
        fig1.add_hline(y=report["resume"]["taille_originale_kb"], line_dash="dash", line_color="red", annotation_text=f"Original: {report['resume']['taille_originale_kb']} KB")
        fig1.update_layout(title="Taille par format (KB)", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = go.Figure(go.Bar(x=formats, y=psnr, marker_color=COLORS, text=[f"{p:.1f} dB" for p in psnr], textposition="auto"))
        fig2.update_layout(title="PSNR par format (dB)", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig2, use_container_width=True)
    col3, col4 = st.columns(2)
    with col3:
        fig3 = go.Figure(go.Bar(x=formats, y=ssim, marker_color=COLORS, text=[f"{s:.4f}" for s in ssim], textposition="auto"))
        fig3.update_layout(title="SSIM par format (0-1)", yaxis=dict(range=[0.9, 1.01]), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        labels = ["Original"] + formats
        values = [report["resume"]["taille_originale_kb"]] + tailles
        fig4 = go.Figure(go.Bar(x=labels, y=values, marker_color=["#E74C3C"]+COLORS, text=[f"{v:.1f} KB" for v in values], textposition="auto"))
        fig4.update_layout(title="Original vs Compresses (KB)", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

def graphiques_dataset(summary):
    items = summary["items"]
    categories = {}
    formats_count = {}
    cat_fmt = {}
    for item in items:
        if item["status"] == "success":
            cat = Path(item["image"]).parent.name
            fmt = item["best_format"]
            categories[cat] = categories.get(cat, 0) + 1
            formats_count[fmt] = formats_count.get(fmt, 0) + 1
            if cat not in cat_fmt:
                cat_fmt[cat] = {}
            cat_fmt[cat][fmt] = cat_fmt[cat].get(fmt, 0) + 1
    st.markdown('<div class="card"><div class="card-title">Graphiques du dataset</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fig1 = go.Figure(go.Pie(labels=list(formats_count.keys()), values=list(formats_count.values()), hole=0.4, marker_colors=COLORS))
        fig1.update_layout(title="Meilleur format global", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = go.Figure(go.Bar(x=list(categories.keys()), y=list(categories.values()), marker_color=COLORS[:len(categories)], text=list(categories.values()), textposition="auto"))
        fig2.update_layout(title="Images par categorie", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig2, use_container_width=True)
    all_formats = list(set(f for c in cat_fmt.values() for f in c.keys()))
    all_cats = list(cat_fmt.keys())
    fig3 = go.Figure()
    for i, fmt in enumerate(all_formats):
        fig3.add_trace(go.Bar(name=fmt, x=all_cats, y=[cat_fmt[cat].get(fmt, 0) for cat in all_cats], marker_color=COLORS[i % len(COLORS)]))
    fig3.update_layout(barmode="group", title="Meilleur format par categorie", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig3, use_container_width=True)
    rows = [{"Image": Path(i["image"]).name, "Categorie": Path(i["image"]).parent.name, "Meilleur format": i["best_format"], "Statut": "OK"} for i in items if i["status"] == "success"]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="card"><div class="card-title">Mode de traitement</div>', unsafe_allow_html=True)
mode = st.radio("", ["Une seule image", "Dossier complet (dataset)"], horizontal=True)
st.markdown("</div>", unsafe_allow_html=True)

if mode == "Une seule image":
    st.markdown('<div class="card"><div class="card-title">Charger une image</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Formats supportes : JPG, JPEG, PNG, WEBP, BMP, TIFF", type=["jpg","jpeg","png","webp","bmp","tiff"])
    st.markdown("</div>", unsafe_allow_html=True)
    if uploaded:
        st.markdown('<div class="card"><div class="card-title">Apercu de l image</div>', unsafe_allow_html=True)
        st.image(uploaded, caption=uploaded.name, use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Nom du fichier", uploaded.name)
        col2.metric("Taille originale", f"{round(uploaded.size/1024, 2)} KB")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Analyser et Compresser cette image"):
            temp_path = "D:\\projet_compression\\temp_" + uploaded.name
            with open(temp_path, "wb") as f:
                f.write(uploaded.getbuffer())
            with st.spinner("Pipeline en cours..."):
                report = run_pipeline(temp_path)
            st.markdown('<div class="card"><div class="card-title">Resultats</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Type detecte", report["resume"]["type_detecte"])
            c2.metric("Format LLM", report["resume"]["format_recommande_llm"])
            c3.metric("Meilleur format", report["resume"]["meilleur_format_selon_metriques"])
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="card"><div class="card-title">Justification IA</div>', unsafe_allow_html=True)
            st.info(report["resume"]["justification_llm"])
            st.markdown("</div>", unsafe_allow_html=True)
            graphiques_image(report)
            st.markdown('<div class="card"><div class="card-title">Metriques de qualite</div>', unsafe_allow_html=True)
            for m in report["details"]["evaluation"]["metrics_by_format"]:
                if m.get("metrics"):
                    with st.expander(f"Format : {m['format']}"):
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("PSNR", m["metrics"]["PSNR_dB"])
                        col2.metric("SSIM", m["metrics"]["SSIM"])
                        col3.metric("MSE", m["metrics"]["MSE"])
                        col4.metric("Compression", f"{m['metrics']['compression_ratio_percent']}%")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="card"><div class="card-title">Rapport JSON</div>', unsafe_allow_html=True)
            st.code(json.dumps(report, indent=2, ensure_ascii=False), language="json")
            st.markdown("</div>", unsafe_allow_html=True)
            os.remove(temp_path)

else:
    st.markdown('<div class="card"><div class="card-title">Configuration du dataset</div>', unsafe_allow_html=True)
    dataset_path = st.text_input("Chemin vers le dossier dataset", value="D:\\projet_compression\\dataset")
    results_path = st.text_input("Chemin vers le dossier results", value="D:\\projet_compression\\results")
    if dataset_path and Path(dataset_path).exists():
        all_images = []
        for ext in [".jpg",".jpeg",".png",".webp",".bmp",".tiff"]:
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
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Lancer le pipeline sur tout le dataset"):
        if not Path(dataset_path).exists():
            st.error("Dossier dataset introuvable !")
        else:
            with st.spinner("Pipeline en cours sur toutes les images..."):
                summary = process_dataset(dataset_path, results_path)
            st.success(f"Pipeline termine ! {summary['success']}/{summary['total_images']} images traitees.")
            if summary["failed"] > 0:
                st.error(f"Echecs : {summary['failed']}")
            graphiques_dataset(summary)
            st.markdown('<div class="card"><div class="card-title">Resultats par image</div>', unsafe_allow_html=True)
            for item in summary["items"]:
                if item["status"] == "success":
                    with st.expander(f"OK - {Path(item['image']).name}"):
                        col1, col2 = st.columns(2)
                        col1.write(f"**Meilleur format :** {item['best_format']}")
                        if item.get("report") and Path(item["report"]).exists():
                            with open(item["report"], "r", encoding="utf-8") as f:
                                rpt = json.load(f)
                            col2.write(f"**Type detecte :** {rpt['resume']['type_detecte']}")
                            col2.write(f"**Format LLM :** {rpt['resume']['format_recommande_llm']}")
                            col2.write(f"**Taille :** {rpt['resume']['taille_originale_kb']} KB")
                            st.info(rpt["resume"]["justification_llm"])
                else:
                    with st.expander(f"ERREUR - {Path(item['image']).name}"):
                        st.error(item.get("error", "Erreur inconnue"))
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="card"><div class="card-title">Rapport global JSON</div>', unsafe_allow_html=True)
            st.code(json.dumps(summary, indent=2, ensure_ascii=False), language="json")
            st.markdown("</div>", unsafe_allow_html=True)