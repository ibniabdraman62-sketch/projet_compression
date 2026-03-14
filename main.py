"""
Pipeline principal : Orchestration de tous les agents
"""
import json
import sys
from pathlib import Path
from agents.agent1_extractor import extract_features
from agents.agent2_classifier import classify_image
from agents.agent3_llm import get_compression_recommendation
from agents.agent4_compressor import compress_image
from agents.agent5_evaluator import calculate_metrics
from agents.agent6_reporter import generate_report

def run_pipeline(image_path: str, output_dir: str = "results") -> dict:
    """
    Lance le pipeline complet sur une image.
    """
    print(f"\n[*] Traitement de : {image_path}")
    print("  -> Agent 1 : Extraction des caracteristiques...")
    features = extract_features(image_path)
    print("  -> Agent 2 : Classification de l'image...")
    classification = classify_image(features)
    print(f"     Type detecte : {classification['image_type']} ({classification['confidence']*100:.0f}%)")
    print("  -> Agent 3 : Recommandation LLM (Gemini)...")
    recommendation = get_compression_recommendation(features, classification)
    reco = recommendation["recommendation"]
    print(f"     Format recommande : {reco['format_recommande']} | Qualite : {reco.get('qualite', 'N/A')}")
    print("  -> Agent 4 : Compression...")
    compression = compress_image(image_path, recommendation, output_dir)
    print("  -> Agent 5 : Evaluation des metriques...")
    evaluation = calculate_metrics(image_path, compression["compressed_files"])
    print("  -> Agent 6 : Generation du rapport...")
    report = generate_report(features, classification, recommendation, compression, evaluation, output_dir)
    print(f"  [OK] Rapport : {report['rapport_sauvegarde']}")
    return report

def run_batch(images_dir: str = "images", output_dir: str = "results"):
    """
    Lance le pipeline sur toutes les images d'un dossier.
    """
    images_path = Path(images_dir)
    extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]
    all_images = []
    for ext in extensions:
        all_images.extend(list(images_path.rglob(f"*{ext}")))
    print(f"\n[*] {len(all_images)} images trouvees dans '{images_dir}'")
    all_reports = []
    for img in all_images:
        try:
            report = run_pipeline(str(img), output_dir)
            all_reports.append(report)
        except Exception as e:
            print(f"  [ERREUR] {img.name} : {e}")
    print(f"\n[OK] Pipeline termine ! {len(all_reports)}/{len(all_images)} images traitees.")
    return all_reports

if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_pipeline(sys.argv[1])
    else:
        run_batch()