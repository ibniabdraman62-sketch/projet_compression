"""
Traitement batch du dataset complet
Usage :
    python process_dataset.py
ou
    python process_dataset.py dataset results
"""

import json
import sys
from pathlib import Path
from main import run_pipeline


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}


def process_dataset(dataset_root: str = "dataset", results_root: str = "results") -> dict:
    dataset_path = Path(dataset_root)
    results_path = Path(results_root)
    results_path.mkdir(parents=True, exist_ok=True)

    summary = {
        "dataset_root": str(dataset_path.resolve()),
        "results_root": str(results_path.resolve()),
        "total_images": 0,
        "success": 0,
        "failed": 0,
        "items": []
    }

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dossier dataset introuvable : {dataset_path}")

    category_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]

    for category_dir in category_dirs:
        for image_path in sorted(category_dir.iterdir()):
            if image_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue

            summary["total_images"] += 1
            print(f"Traitement : {image_path}")

            try:
                report = run_pipeline(str(image_path), output_dir=results_root)
                summary["success"] += 1
                summary["items"].append({
                    "image": str(image_path),
                    "status": "success",
                    "report": report.get("rapport_sauvegarde"),
                    "best_format": report["resume"]["meilleur_format_selon_metriques"]
                })
            except Exception as e:
                summary["failed"] += 1
                summary["items"].append({
                    "image": str(image_path),
                    "status": "failed",
                    "error": str(e)
                })

    summary_file = results_path / "summary_dataset.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nRésumé sauvegardé : {summary_file}")
    print(f"Images traitées : {summary['total_images']}")
    print(f"Succès : {summary['success']}")
    print(f"Échecs : {summary['failed']}")

    return summary


if __name__ == "__main__":
    dataset_root = sys.argv[1] if len(sys.argv) > 1 else "dataset"
    results_root = sys.argv[2] if len(sys.argv) > 2 else "results"

    try:
        result = process_dataset(dataset_root, results_root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2, ensure_ascii=False))
        sys.exit(1)