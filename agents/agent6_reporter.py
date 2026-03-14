"""
Agent 6 : Générateur de rapport
Rôle : Assembler tous les résultats en un rapport JSON complet
Entrée : Résultats de tous les agents précédents
Sortie : Rapport JSON final sauvegardé sur disque
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def generate_report(
    features: dict,
    classification: dict,
    recommendation: dict,
    compression: dict,
    evaluation: dict,
    output_dir: str = "results"
) -> dict:

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = Path(features["metadata"]["filename"]).stem

    best_format = None
    best_score = -10**9

    for metric in evaluation["metrics_by_format"]:
        if metric.get("metrics"):
            score = metric["metrics"]["quality_score_combined"]
            if score > best_score:
                best_score = score
                best_format = metric["format"]

    report = {
        "rapport_id": f"{image_name}_{timestamp}",
        "date_analyse": datetime.now().isoformat(),
        "image_analysee": features["metadata"]["filename"],
        "resume": {
            "type_detecte": classification["image_type"],
            "confiance_classification": classification["confidence"],
            "format_recommande_llm": recommendation["recommendation"]["format_recommande"],
            "justification_llm": recommendation["recommendation"]["justification"],
            "meilleur_format_selon_metriques": best_format,
            "taille_originale_kb": features["metadata"]["file_size_kb"]
        },
        "details": {
            "caracteristiques": features,
            "classification": classification,
            "recommandation_llm": recommendation,
            "compression": compression,
            "evaluation": evaluation
        }
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_file = output_path / f"rapport_{image_name}.json"

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    report["rapport_sauvegarde"] = str(report_file)
    print(f"Rapport sauvegardé : {report_file}", file=sys.stderr)

    return report


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print(json.dumps({
            "error": "Usage: python agent6_reporter.py '<features>' '<classification>' '<recommendation>' '<compression>' '<evaluation>'"
        }))
        sys.exit(1)

    f = [json.loads(sys.argv[i]) for i in range(1, 6)]
    result = generate_report(f[0], f[1], f[2], f[3], f[4])
    print(json.dumps(result, indent=2, ensure_ascii=False))