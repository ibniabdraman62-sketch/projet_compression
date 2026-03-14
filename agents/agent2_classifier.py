"""
Agent 2 : Classificateur
Rôle : Déterminer le type de l'image
Entrée : JSON de l'Agent 1
Sortie : JSON avec le type détecté
"""

import json
import sys


def classify_image(features: dict) -> dict:

    scores = {
        "photo": 0,
        "document": 0,
        "graphique": 0,
        "screenshot": 0,
        "illustration": 0
    }

    metadata = features["metadata"]
    color = features["color_stats"]
    complexity = features["complexity"]
    hints = features["content_hints"]

    entropy = complexity["entropy"]
    edge_density = complexity["edge_density"]
    sharpness = complexity["sharpness_laplacian"]
    text_ratio = hints["probable_text_ratio"]
    is_grayscale = color["is_grayscale"]
    width = metadata["width"]
    height = metadata["height"]

    # Règles pour PHOTO
    if entropy > 6.5:
        scores["photo"] += 3
    if not is_grayscale and color["std_r"] > 40:
        scores["photo"] += 2
    if sharpness > 200:
        scores["photo"] += 1
    if edge_density < 0.15:
        scores["photo"] += 1

    # Règles pour DOCUMENT
    if text_ratio > 0.3:
        scores["document"] += 4
    if is_grayscale:
        scores["document"] += 2
    if entropy < 5.0:
        scores["document"] += 2
    if edge_density > 0.15 and entropy < 6.0:
        scores["document"] += 1

    # Règles pour GRAPHIQUE
    if entropy < 4.5:
        scores["graphique"] += 3
    if edge_density > 0.08 and sharpness > 300:
        scores["graphique"] += 2
    if color["std_r"] < 30 and color["std_g"] < 30:
        scores["graphique"] += 2

    # Règles pour SCREENSHOT
    common_resolutions = [(1920, 1080), (1366, 768), (2560, 1440), (1280, 720)]
    if (width, height) in common_resolutions:
        scores["screenshot"] += 4
    if edge_density > 0.12 and entropy > 5.0:
        scores["screenshot"] += 2
    if text_ratio > 0.15 and not is_grayscale:
        scores["screenshot"] += 1

    # Règles pour ILLUSTRATION
    if color["mean_r"] > 180 or color["mean_g"] > 180 or color["mean_b"] > 180:
        scores["illustration"] += 2
    if entropy < 5.5 and edge_density > 0.1:
        scores["illustration"] += 2
    if color["std_r"] < 50 and not is_grayscale:
        scores["illustration"] += 1

    # Déterminer le gagnant
    best_type = max(scores, key=scores.get)
    total_score = sum(scores.values())
    confidence = round(scores[best_type] / total_score, 2) if total_score > 0 else 0

    result = {
        "agent": "Agent2_Classifier",
        "image_type": best_type,
        "confidence": confidence,
        "scores": scores,
        "image_path": features["image_path"]
    }

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python agent2_classifier.py '<json_string>'"}))
        sys.exit(1)
    features = json.loads(sys.argv[1])
    result = classify_image(features)
    print(json.dumps(result, indent=2))