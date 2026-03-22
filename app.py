import streamlit as st
import os, sys, json
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd

os.chdir("D:\\projet_compression")
sys.path.insert(0, "D:\\projet_compression")

from main import run_pipeline
from process_dataset import process_dataset

st.set_page_config(page_title="Compression Intelligente", page_icon="Image", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364) !important; }
.card { background: rgba(255,255,255,0.08); border-radius: 16px; padding: 25px; margin: 15px 0; border: 1px solid rgba(76,161,175,0.4); backdrop-filter: blur(10px); }
.card-title { font-size: 1.2em; font-weight: bold; color: #4CA1AF; margin-bottom: 15px; border-bottom: 2px solid #4CA1AF; padding-bottom: 8px; }
.stButton > button { background: linear-gradient(135deg, #4CA1AF, #2C3E50) !important; color: white !important; border: none !important; border-radius: 25px !important; padding: 12px 35px !important; font-size: 1.1em !important; width: 100% !important; box-shadow: 0 4px 15px rgba(76,161,175,0.4) !important; }
.stButton > button:hover { transform: translateY(-2px) !important; }
div[role="radiogroup"] label { background: rgba(26,58,74,0.7) !important; border-radius: 10px !important; padding: 8px 20px !important; margin: 5px !important; color: white !important; border: 2px solid #4CA1AF !important; }
h1, h2, h3 { color: white !important; }
p, label { color: rgba(255,255,255,0.9) !important; }
.stTextInput input { background: rgba(255,255,255,0.1) !important; color: white !important; border: 1px solid #4CA1AF !important; border-radius: 10px !important; }
[data-testid="stMetricValue"] { color: #4CA1AF !important; font-weight: bold !important; font-size: 1.4em !important; }
[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.8) !important; }
[data-testid="stFileUploader"] { background: rgba(76,161,175,0.1) !important; border: 2px dashed #4CA1AF !important; border-radius: 15px !important; padding: 15px !important; }
[data-testid="stSidebar"] { background: rgba(15,32,39,0.95) !important; border-right: 1px solid rgba(76,161,175,0.3) !important; }
.streamlit-expanderHeader { background: rgba(76,161,175,0.2) !important; border-radius: 10px !important; color: white !important; }
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0;">
    <h2 style="color: #4CA1AF; font-size: 1.4em;">Compression IA</h2>
    <p style="color: rgba(255,255,255,0.6); font-size: 0.85em;">Architecture Multi-Agents<br>Google Gemini 2.5 Flash</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("### Informations")
    st.markdown("""
    <div style="color: rgba(255,255,255,0.8); font-size: 0.9em; line-height: 1.8;">
    <b style="color:#4CA1AF;">6 Agents</b> Python autonomes<br>
    <b style="color:#4CA1AF;">6 Formats</b> de compression<br>
    <b style="color:#4CA1AF;">3 Metriques</b> de qualite<br>
    <b style="color:#4CA1AF;">35 Images</b> testees (100%)<br>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("### Score combine")
    st.markdown("""
    <div style="font-size:0.85em; color: rgba(255,255,255,0.7);">
    <span style="background:#27AE60;color:white;padding:2px 8px;border-radius:10px;">Excellent</span> >= 0.80<br><br>
    <span style="background:#2E75B6;color:white;padding:2px 8px;border-radius:10px;">Bon</span> >= 0.65<br><br>
    <span style="background:#E67E22;color:white;padding:2px 8px;border-radius:10px;">Acceptable</span> >= 0.50<br><br>
    <span style="background:#E74C3C;color:white;padding:2px 8px;border-radius:10px;">Insuffisant</span> < 0.50
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("<p style='color:rgba(255,255,255,0.4);font-size:0.75em;text-align:center;'>FSTM — Licence IRM — 2025-2026<br>Prof. Abdellah ADIB</p>", unsafe_allow_html=True)

# HEADER
st.markdown("""
<div style="text-align:center; padding: 25px 0 10px 0;">
<h1 style="color: white; font-size: 2.3em; font-weight: bold; text-shadow: 0 2px 10px rgba(76,161,175,0.5);">Systeme Intelligent de Compression des Images</h1>
<p style="color: rgba(255,255,255,0.7); font-size: 1.1em;">Architecture Multi-Agents + IA Generative (Google Gemini 2.5 Flash)</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Agents", "6", "autonomes")
col2.metric("Formats", "6", "JPEG/PNG/WEBP/TIFF/JP2/JPEG_Q60")
col3.metric("Metriques", "3", "PSNR/SSIM/MSE")
col4.metric("Succes", "100%", "35/35 images")
st.divider()

# COULEURS ET HELPERS
COLORS = ["#4CA1AF", "#2C3E50", "#27AE60", "#E74C3C", "#F39C12", "#9B59B6"]
COLORS_PIE = ["#4CA1AF", "#27AE60", "#E74C3C", "#F39C12", "#9B59B6", "#2C3E50"]

def get_badge(label):
    colors = {"Excellent": "#27AE60", "Bon": "#2E75B6", "Acceptable": "#E67E22", "Insuffisant": "#E74C3C"}
    c = colors.get(label, "#888")
    return f'<span style="background:{c};color:white;padding:3px 12px;border-radius:15px;font-weight:bold;font-size:0.85em;">{label}</span>'

def layout_plotly(title):
    return dict(title=dict(text=title, font=dict(color="white", size=13)),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"), margin=dict(t=40, b=20, l=20, r=20),
                xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)"))

def graphiques_image(report):
    metrics = report["details"]["evaluation"]["metrics_by_format"]
    formats, tailles, psnr_vals, ssim_vals, scores, interpretations = [], [], [], [], [], []
    for m in metrics:
        if not m.get("metrics"):
            continue
        formats.append(m["format"])
        tailles.append(m["compressed_size_kb"])
        p = m["metrics"]["PSNR_dB"]
        psnr_vals.append(100 if p == "Infini" else float(p))
        ssim_vals.append(float(m["metrics"]["SSIM"]))
        scores.append(float(m["metrics"].get("quality_score_combined", 0)))
        interpretations.append(m.get("interpretation", {}).get("quality", "N/A"))
    meilleur_idx = scores.index(max(scores)) if scores else 0
    bar_colors = [COLORS[i % len(COLORS)] for i in range(len(formats))]
    bar_colors_meilleur = ["#F39C12" if i == meilleur_idx else COLORS[i % len(COLORS)] for i in range(len(formats))]
    st.markdown('<div class="card"><div class="card-title">Graphiques de comparaison</div>', unsafe_allow_html=True)
    if formats:
        st.markdown(f'<p style="color:white;">Meilleur format : <span style="background:#F39C12;color:white;padding:3px 12px;border-radius:15px;font-weight:bold;">{formats[meilleur_idx]}</span> Score : <b style="color:#4CA1AF;">{scores[meilleur_idx]:.4f}</b> {get_badge(interpretations[meilleur_idx])}</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fig1 = go.Figure(go.Bar(x=formats, y=tailles, marker_color=bar_colors_meilleur, text=[f"{t:.1f} KB" for t in tailles], textposition="auto"))
        fig1.add_hline(y=report["resume"]["taille_originale_kb"], line_dash="dash", line_color="#E74C3C", annotation_text=f"Original: {report['resume']['taille_originale_kb']} KB", annotation_font_color="white")
        fig1.update_layout(**layout_plotly("Taille par format (KB)"))
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = go.Figure(go.Bar(x=formats, y=psnr_vals, marker_color=bar_colors, text=[f"{p:.1f} dB" for p in psnr_vals], textposition="auto"))
        fig2.add_hline(y=40, line_dash="dot", line_color="#27AE60", annotation_text="Seuil excellent (40dB)", annotation_font_color="#27AE60")
        fig2.update_layout(**layout_plotly("PSNR par format (dB)"))
        st.plotly_chart(fig2, use_container_width=True)
    col3, col4 = st.columns(2)
    with col3:
        fig3 = go.Figure(go.Bar(x=formats, y=ssim_vals, marker_color=bar_colors, text=[f"{s:.4f}" for s in ssim_vals], textposition="auto"))
        fig3.update_layout(**layout_plotly("SSIM par format (0-1)"))
        fig3.update_yaxes(range=[min(ssim_vals)-0.02 if ssim_vals else 0, 1.02])
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        fig4 = go.Figure(go.Bar(x=formats, y=scores, marker_color=bar_colors_meilleur, text=[f"{s:.4f}" for s in scores], textposition="auto"))
        fig4.add_hline(y=0.80, line_dash="dot", line_color="#27AE60", annotation_text="Excellent (0.80)", annotation_font_color="#27AE60")
        fig4.add_hline(y=0.65, line_dash="dot", line_color="#2E75B6", annotation_text="Bon (0.65)", annotation_font_color="#2E75B6")
        fig4.update_layout(**layout_plotly("Score combine par format"))
        st.plotly_chart(fig4, use_container_width=True)
    if len(formats) >= 3:
        st.markdown("#### Graphique Radar — Vue globale")
        categories_radar = ["PSNR norm.", "SSIM", "Compression"]
        fig_radar = go.Figure()
        taux_vals = []
        for m in report["details"]["evaluation"]["metrics_by_format"]:
            if m.get("metrics"):
                taux_vals.append(max(m["metrics"]["compression_ratio_percent"], 0) / 100)
        for i, fmt in enumerate(formats):
            psnr_n = min(psnr_vals[i], 50) / 50
            vals = [psnr_n, ssim_vals[i], taux_vals[i] if i < len(taux_vals) else 0]
            vals_closed = vals + [vals[0]]
            cats_closed = categories_radar + [categories_radar[0]]
            fig_radar.add_trace(go.Scatterpolar(r=vals_closed, theta=cats_closed,
                fill="toself", name=fmt, line=dict(color=COLORS[i % len(COLORS)]),
                fillcolor=COLORS[i % len(COLORS)], opacity=0.3))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,1], gridcolor="rgba(255,255,255,0.2)", color="white"),
                       angularaxis=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"), legend=dict(font=dict(color="white")),
            title=dict(text="Comparaison globale des formats", font=dict(color="white", size=13)))
        st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown("#### Tableau comparatif")
    rows_tab = []
    for i, m in enumerate(report["details"]["evaluation"]["metrics_by_format"]):
        if m.get("metrics"):
            est_meilleur = "MEILLEUR" if i == meilleur_idx else ""
            interp = m.get("interpretation", {}).get("quality", "N/A")
            rows_tab.append({
                "Format": est_meilleur + " " + m["format"],
                "Taille (KB)": m["compressed_size_kb"],
                "PSNR (dB)": m["metrics"]["PSNR_dB"],
                "SSIM": m["metrics"]["SSIM"],
                "MSE": m["metrics"]["MSE"],
                "Compression %": m["metrics"]["compression_ratio_percent"],
                "Score": m["metrics"].get("quality_score_combined", "N/A"),
                "Qualite": interp
            })
    st.dataframe(pd.DataFrame(rows_tab), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

def graphiques_dataset(summary):
    items = summary["items"]
    categories, formats_count, cat_fmt = {}, {}, {}
    for item in items:
        if item["status"] == "success":
            cat = Path(item["image"]).parent.name
            fmt = item["best_format"]
            categories[cat] = categories.get(cat, 0) + 1
            formats_count[fmt] = formats_count.get(fmt, 0) + 1
            if cat not in cat_fmt: cat_fmt[cat] = {}
            cat_fmt[cat][fmt] = cat_fmt[cat].get(fmt, 0) + 1
    st.markdown('<div class="card"><div class="card-title">Graphiques du dataset</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fig1 = go.Figure(go.Pie(labels=list(formats_count.keys()), values=list(formats_count.values()), hole=0.45, marker_colors=COLORS_PIE, textinfo="label+percent", textfont=dict(color="white", size=12)))
        fig1.update_layout(**layout_plotly("Meilleur format global"))
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = go.Figure(go.Bar(x=list(categories.keys()), y=list(categories.values()), marker_color=COLORS[:len(categories)], text=list(categories.values()), textposition="auto", textfont=dict(color="white")))
        fig2.update_layout(**layout_plotly("Images par categorie"))
        st.plotly_chart(fig2, use_container_width=True)
    all_formats = list(set(f for c in cat_fmt.values() for f in c.keys()))
    all_cats = list(cat_fmt.keys())
    fig3 = go.Figure()
    for i, fmt in enumerate(all_formats):
        fig3.add_trace(go.Bar(name=fmt, x=all_cats, y=[cat_fmt[cat].get(fmt, 0) for cat in all_cats], marker_color=COLORS[i % len(COLORS)]))
    fig3.update_layout(barmode="group", **layout_plotly("Meilleur format par categorie"))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("#### Tableau recapitulatif")
    rows = []
    for item in items:
        if item["status"] == "success":
            rows.append({"Image": Path(item["image"]).name, "Categorie": Path(item["image"]).parent.name, "Meilleur format": item["best_format"], "Statut": "Succes"})
        else:
            rows.append({"Image": Path(item["image"]).name, "Categorie": Path(item["image"]).parent.name, "Meilleur format": "N/A", "Statut": "Echec"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# MODE DE TRAITEMENT
st.markdown('<div class="card"><div class="card-title">Mode de traitement</div>', unsafe_allow_html=True)
mode = st.radio("", ["Une seule image", "Dossier complet (dataset)"], horizontal=True)
st.markdown("</div>", unsafe_allow_html=True)

# MODE 1 : IMAGE UNIQUE
if mode == "Une seule image":
    st.markdown('<div class="card"><div class="card-title">Charger une image</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Formats supportes : JPG, JPEG, PNG, WEBP, BMP, TIFF", type=["jpg","jpeg","png","webp","bmp","tiff"])
    st.markdown("</div>", unsafe_allow_html=True)
    if uploaded:
        st.markdown('<div class="card"><div class="card-title">Apercu de l image</div>', unsafe_allow_html=True)
        col_img, col_info = st.columns([2, 1])
        with col_img:
            st.image(uploaded, caption=uploaded.name, use_container_width=True)
        with col_info:
            st.metric("Fichier", uploaded.name)
            st.metric("Taille", f"{round(uploaded.size/1024, 2)} KB")
            st.metric("Format", Path(uploaded.name).suffix.upper())
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Analyser et Compresser cette image"):
            temp_path = "D:\\projet_compression\\temp_" + uploaded.name
            with open(temp_path, "wb") as f:
                f.write(uploaded.getbuffer())
            progress = st.progress(0, text="Initialisation du pipeline...")
            progress.progress(15, text="Agent 1 : Extraction des caracteristiques...")
            with st.spinner("Pipeline en cours..."):
                report = run_pipeline(temp_path)
            progress.progress(100, text="Pipeline termine !")
            st.markdown('<div class="card"><div class="card-title">Resultats de l analyse</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Type detecte", report["resume"]["type_detecte"])
            c2.metric("Format LLM", report["resume"]["format_recommande_llm"])
            c3.metric("Meilleur format", report["resume"]["meilleur_format_selon_metriques"])
            c4.metric("Taille originale", f'{report["resume"]["taille_originale_kb"]} KB')
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="card"><div class="card-title">Justification de l IA (Gemini)</div>', unsafe_allow_html=True)
            st.info(report["resume"]["justification_llm"])
            st.markdown("</div>", unsafe_allow_html=True)
            graphiques_image(report)
            st.markdown('<div class="card"><div class="card-title">Metriques detaillees par format</div>', unsafe_allow_html=True)
            for m in report["details"]["evaluation"]["metrics_by_format"]:
                if m.get("metrics"):
                    interp = m.get("interpretation", {}).get("quality", "N/A")
                    badge = get_badge(interp)
                    is_best = m["format"] == report["resume"]["meilleur_format_selon_metriques"]
                    icon = "MEILLEUR " if is_best else ""
                    with st.expander(f"{icon}Format : {m['format']}"):
                        st.markdown(f"Qualite : {badge}", unsafe_allow_html=True)
                        col1, col2, col3, col4, col5 = st.columns(5)
                        col1.metric("PSNR", m["metrics"]["PSNR_dB"])
                        col2.metric("SSIM", m["metrics"]["SSIM"])
                        col3.metric("MSE", m["metrics"]["MSE"])
                        col4.metric("Compression", f'{m["metrics"]["compression_ratio_percent"]}%')
                        col5.metric("Score", m["metrics"].get("quality_score_combined", "N/A"))
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="card"><div class="card-title">Rapport JSON complet</div>', unsafe_allow_html=True)
            st.code(json.dumps(report, indent=2, ensure_ascii=False), language="json")
            st.markdown("</div>", unsafe_allow_html=True)
            os.remove(temp_path)

# MODE 2 : DATASET
else:
    st.markdown('<div class="card"><div class="card-title">Configuration du dataset</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        dataset_path = st.text_input("Chemin dataset", value="D:\\projet_compression\\dataset")
    with col_p2:
        results_path = st.text_input("Chemin resultats", value="D:\\projet_compression\\results")
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
        icons = {"photos": "Photos", "documents": "Documents", "graphiques": "Graphiques", "screenshots": "Screenshots"}
        for i, (cat, count) in enumerate(categories.items()):
            icon = icons.get(cat, cat)
            cols[i].metric(icon, f"{count} images")
    else:
        st.warning("Dossier dataset introuvable !")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Lancer le pipeline sur tout le dataset"):
        if not Path(dataset_path).exists():
            st.error("Dossier dataset introuvable !")
        else:
            progress = st.progress(0, text="Demarrage du pipeline dataset...")
            with st.spinner("Pipeline en cours sur toutes les images..."):
                summary = process_dataset(dataset_path, results_path)
            progress.progress(100, text="Pipeline termine !")
            total = summary["total_images"]
            succes = summary["success"]
            echecs = summary["failed"]
            taux = round(succes/total*100, 1) if total > 0 else 0
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", total)
            col2.metric("Succes", succes)
            col3.metric("Echecs", echecs)
            col4.metric("Taux", f"{taux}%")
            if echecs > 0:
                st.error(f"{echecs} echec(s) detecte(s)")
            else:
                st.success(f"Pipeline termine ! {succes}/{total} images traitees avec succes (100%)")
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