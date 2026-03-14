"""
Agent 5 : Évaluateur de qualité
Rôle : Calculer les métriques de qualité (PSNR, SSIM, MSE, taux de compression)
Entrée : Image originale + images compressées (Agent 4)
Sortie : JSON avec toutes les métriques
"""

import json
import sys
import numpy as np
from pathlib import Path
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse


def calculate_metrics(original_path: str, compressed_files: list) -> dict:
    original_img = Image.open(original_path).convert("RGB")
    original_array = np.array(original_img)
    original_size = Path(original_path).stat().st_size

    metrics_results = []

    for compressed in compressed_files:
        if not compressed.get("success") or not compressed.get("path"):
            metrics_results.append({
                "format": compressed["format"],
                "error": "Compression failed",
                "metrics": None
            })
            continue

        try:
            compressed_img = Image.open(compressed["path"]).convert("RGB")

            if compressed_img.size != original_img.size:
                compressed_img = compressed_img.resize(original_img.size, Image.LANCZOS)

            compressed_array = np.array(compressed_img)
            compressed_size = Path(compressed["path"]).stat().st_size

            mse_value = float(mse(original_array, compressed_array))

            if mse_value == 0:
                psnr_value = float("inf")
            else:
                psnr_value = float(psnr(original_array, compressed_array, data_range=255))

            ssim_value = float(
                ssim(original_array, compressed_array, channel_axis=2, data_range=255)
            )

            compression_ratio = round((1 - compressed_size / original_size) * 100, 2)
            quality_score = round(ssim_value * (1 + compression_ratio / 100), 4)

            if psnr_value == float("inf") or psnr_value > 40:
                quality_label = "Excellente"
            elif psnr_value > 30:
                quality_label = "Bonne"
            elif psnr_value > 20:
                quality_label = "Acceptable"
            else:
                quality_label = "Mauvaise"

            if compression_ratio > 70:
                compression_label = "Fort"
            elif compression_ratio > 40:
                compression_label = "Moyen"
            else:
                compression_label = "Faible"

            metrics_results.append({
                "format": compressed["format"],
                "original_size_kb": round(original_size / 1024, 2),
                "compressed_size_kb": round(compressed_size / 1024, 2),
                "metrics": {
                    "MSE": round(mse_value, 4),
                    "PSNR_dB": "Infini" if psnr_value == float("inf") else round(psnr_value, 2),
                    "SSIM": round(ssim_value, 4),
                    "compression_ratio_percent": compression_ratio,
                    "quality_score_combined": quality_score
                },
                "interpretation": {
                    "quality": quality_label,
                    "compression": compression_label
                }
            })

        except Exception as e:
            metrics_results.append({
                "format": compressed["format"],
                "error": str(e),
                "metrics": None
            })

    result = {
        "agent": "Agent5_Evaluator",
        "image_path": original_path,
        "metrics_by_format": metrics_results
    }

    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python agent5_evaluator.py '<original_path>' '<compressed_files_json>'"
        }))
        sys.exit(1)

    original = sys.argv[1]
    compressed = json.loads(sys.argv[2])
    result = calculate_metrics(original, compressed)
    print(json.dumps(result, indent=2, ensure_ascii=False))