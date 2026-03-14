"""
Agent 3 : Recommandeur LLM (Gemini) avec fallback local
Rôle : Générer une recommandation de compression au format JSON
Entrée : Features + classification
Sortie : JSON de recommandation
"""

import json
import sys
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "TIFF", "JPEG2000"}


def build_fallback_recommendation(features: dict, classification: dict) -> dict:
    image_type = classification["image_type"]
    text_ratio = features["content_hints"]["probable_text_ratio"]
    high_contrast = features["content_hints"]["high_contrast"]
    is_grayscale = features["color_stats"]["is_grayscale"]

    # Heuristiques simples et explicables
    if image_type == "document" or text_ratio > 0.45:
        format_recommande = "PNG"
        formats_alternatifs = ["WEBP", "JPEG"]
        qualite = 90
        sans_perte = True
        usage_recommande = "archive"
        niveau_compression = "moyen"
        justification = (
            "Fallback local : image à forte composante textuelle. "
            "PNG est privilégié pour préserver la lisibilité sans perte."
        )

    elif image_type == "screenshot":
        format_recommande = "WEBP"
        formats_alternatifs = ["PNG", "JPEG"]
        qualite = 85
        sans_perte = False
        usage_recommande = "web"
        niveau_compression = "moyen"
        justification = (
            "Fallback local : screenshot détecté. "
            "WEBP offre un bon compromis entre netteté des interfaces et taille du fichier."
        )

    elif image_type == "graphique":
        format_recommande = "PNG"
        formats_alternatifs = ["WEBP", "TIFF"]
        qualite = 95
        sans_perte = True
        usage_recommande = "archive"
        niveau_compression = "faible"
        justification = (
            "Fallback local : graphique/diagramme détecté. "
            "PNG est recommandé pour conserver les bords nets et les formes."
        )

    elif image_type == "illustration":
        format_recommande = "WEBP"
        formats_alternatifs = ["PNG", "JPEG"]
        qualite = 88
        sans_perte = False
        usage_recommande = "web"
        niveau_compression = "moyen"
        justification = (
            "Fallback local : illustration détectée. "
            "WEBP est choisi pour son bon compromis qualité/taille."
        )

    else:  # photo par défaut
        if high_contrast or text_ratio > 0.20 or is_grayscale:
            format_recommande = "WEBP"
            formats_alternatifs = ["JPEG", "PNG"]
            qualite = 82
            sans_perte = False
            usage_recommande = "web"
            niveau_compression = "moyen"
            justification = (
                "Fallback local : photo avec contraste élevé ou présence de texte. "
                "WEBP limite mieux les artefacts que JPEG tout en restant compact."
            )
        else:
            format_recommande = "JPEG"
            formats_alternatifs = ["WEBP", "PNG"]
            qualite = 85
            sans_perte = False
            usage_recommande = "web"
            niveau_compression = "moyen"
            justification = (
                "Fallback local : photo standard. "
                "JPEG reste un choix simple et compatible pour les contenus photographiques."
            )

    return {
        "format_recommande": format_recommande,
        "formats_alternatifs": formats_alternatifs,
        "qualite": qualite,
        "sans_perte": sans_perte,
        "redimensionner": False,
        "nouvelle_resolution": None,
        "justification": justification,
        "usage_recommande": usage_recommande,
        "niveau_compression": niveau_compression
    }


def sanitize_recommendation(recommendation: dict) -> dict:
    if recommendation.get("format_recommande") not in ALLOWED_FORMATS:
        recommendation["format_recommande"] = "WEBP"

    recommendation["formats_alternatifs"] = [
        fmt for fmt in recommendation.get("formats_alternatifs", [])
        if fmt in ALLOWED_FORMATS and fmt != recommendation["format_recommande"]
    ]

    # Compléter si la liste est vide
    if not recommendation["formats_alternatifs"]:
        recommendation["formats_alternatifs"] = [
            fmt for fmt in ["JPEG", "PNG", "WEBP", "TIFF", "JPEG2000"]
            if fmt != recommendation["format_recommande"]
        ][:2]

    return recommendation


def get_compression_recommendation(features: dict, classification: dict) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        recommendation = build_fallback_recommendation(features, classification)
        recommendation = sanitize_recommendation(recommendation)
        return {
            "agent": "Agent3_LLM",
            "image_path": features["image_path"],
            "image_type": classification["image_type"],
            "recommendation": recommendation,
            "llm_model": None,
            "source_recommandation": "fallback_local",
            "fallback_reason": "GEMINI_API_KEY introuvable"
        }

    prompt = f"""
Tu es un expert en compression d'images numériques.

TYPE D'IMAGE DÉTECTÉ : {classification['image_type']} (confiance: {classification['confidence']})

CARACTÉRISTIQUES TECHNIQUES :
- Dimensions : {features['metadata']['width']}x{features['metadata']['height']} pixels
- Taille originale : {features['metadata']['file_size_kb']} KB
- Format actuel : {features['metadata']['format']}
- Est en niveaux de gris : {features['color_stats']['is_grayscale']}

COMPLEXITÉ VISUELLE :
- Densité de contours : {features['complexity']['edge_density']}
- Netteté : {features['complexity']['sharpness_laplacian']}
- Entropie : {features['complexity']['entropy']}

INDICES DE CONTENU :
- Ratio de texte probable : {features['content_hints']['probable_text_ratio']}
- Fort contraste : {features['content_hints']['high_contrast']}

IMPORTANT :
- Réponds UNIQUEMENT en JSON valide.
- Les seuls formats autorisés sont : JPEG, PNG, WEBP, TIFF, JPEG2000.
- "format_recommande" doit être uniquement l’un de ces formats.
- "formats_alternatifs" doit contenir seulement des valeurs parmi : JPEG, PNG, WEBP, TIFF, JPEG2000.
- N'utilise jamais AVIF, GIF, BMP, HEIF ou un autre format.

Utilise exactement cette structure :
{{
  "format_recommande": "JPEG",
  "formats_alternatifs": ["PNG", "WEBP"],
  "qualite": 85,
  "sans_perte": false,
  "redimensionner": false,
  "nouvelle_resolution": null,
  "justification": "Explication détaillée de tes choix",
  "usage_recommande": "web",
  "niveau_compression": "moyen"
}}
"""

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )

        response_text = response.text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[len("```json"):].strip()
        if response_text.startswith("```"):
            response_text = response_text[len("```"):].strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()

        recommendation = json.loads(response_text)
        recommendation = sanitize_recommendation(recommendation)

        return {
            "agent": "Agent3_LLM",
            "image_path": features["image_path"],
            "image_type": classification["image_type"],
            "recommendation": recommendation,
            "llm_model": "gemini-3-flash-preview",
            "source_recommandation": "gemini"
        }

    except Exception as e:
        recommendation = build_fallback_recommendation(features, classification)
        recommendation = sanitize_recommendation(recommendation)

        return {
            "agent": "Agent3_LLM",
            "image_path": features["image_path"],
            "image_type": classification["image_type"],
            "recommendation": recommendation,
            "llm_model": "gemini-3-flash-preview",
            "source_recommandation": "fallback_local",
            "fallback_reason": str(e)
        }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python agent3_llm.py '<features_json>' '<classification_json>'"
        }, ensure_ascii=False))
        sys.exit(1)

    features = json.loads(sys.argv[1])
    classification = json.loads(sys.argv[2])

    try:
        result = get_compression_recommendation(features, classification)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2, ensure_ascii=False))
        sys.exit(1)