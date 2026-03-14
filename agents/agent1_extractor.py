"""
Agent 1 : Extracteur de caractéristiques
Rôle : Analyser une image et extraire ses caractéristiques visuelles et techniques
Entrée : Chemin vers une image
Sortie : JSON avec toutes les caractéristiques
"""

import json
import sys
import numpy as np
import cv2
from PIL import Image
from pathlib import Path


def extract_features(image_path: str) -> dict:
    path = Path(image_path)
    pil_img = Image.open(image_path)
    cv_img = cv2.imread(image_path)

    # 1. Métadonnées
    metadata = {
        "filename": path.name,
        "format": pil_img.format,
        "mode": pil_img.mode,
        "width": pil_img.width,
        "height": pil_img.height,
        "total_pixels": pil_img.width * pil_img.height,
        "file_size_bytes": path.stat().st_size,
        "file_size_kb": round(path.stat().st_size / 1024, 2),
        "aspect_ratio": round(pil_img.width / pil_img.height, 3),
        "color_depth": len(pil_img.getbands()) * 8
    }

    # 2. Statistiques colorimétriques
    img_array = np.array(pil_img.convert("RGB"))
    r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]

    color_stats = {
        "mean_r": round(float(np.mean(r)), 2),
        "mean_g": round(float(np.mean(g)), 2),
        "mean_b": round(float(np.mean(b)), 2),
        "std_r": round(float(np.std(r)), 2),
        "std_g": round(float(np.std(g)), 2),
        "std_b": round(float(np.std(b)), 2),
        "is_grayscale": bool(np.allclose(r, g) and np.allclose(g, b))
    }

    # 3. Complexité visuelle
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_density = round(float(np.sum(edges > 0) / edges.size), 4)
    laplacian_var = round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_norm = hist / hist.sum()
    hist_norm = hist_norm[hist_norm > 0]
    entropy = round(float(-np.sum(hist_norm * np.log2(hist_norm))), 4)

    complexity = {
        "edge_density": edge_density,
        "sharpness_laplacian": laplacian_var,
        "entropy": entropy,
        "is_sharp": bool(laplacian_var > 100)
    }

    # 4. Indices de contenu
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text_ratio = round(float(np.sum(binary == 0) / binary.size), 4)

    content_hints = {
        "probable_text_ratio": text_ratio,
        "has_many_edges": bool(edge_density > 0.1),
        "high_contrast": bool(np.std(img_array) > 60)
    }

    result = {
        "agent": "Agent1_Extractor",
        "image_path": str(path.absolute()),
        "metadata": metadata,
        "color_stats": color_stats,
        "complexity": complexity,
        "content_hints": content_hints
    }

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python agent1_extractor.py <image_path>"}))
        sys.exit(1)
    result = extract_features(sys.argv[1])
    print(json.dumps(result, indent=2))