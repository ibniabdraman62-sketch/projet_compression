"""
Agent 4 : Compresseur
Rôle : Appliquer la compression sur plusieurs formats supportés
Entrée : Image originale + recommandations (Agent 3)
Sortie : Images compressées + métadonnées
"""

import json
import sys
from pathlib import Path
from PIL import Image


SUPPORTED_FORMATS = ["JPEG", "PNG", "WEBP", "TIFF", "JPEG2000"]
EXTENSIONS = {
    "JPEG": "jpeg",
    "PNG": "png",
    "WEBP": "webp",
    "TIFF": "tiff",
    "JPEG2000": "jp2"
}


def compress_image(image_path: str, recommendation: dict, output_dir: str = "results") -> dict:
    path = Path(image_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    img = Image.open(image_path)

    # Convertir en RGB si nécessaire
    if img.mode in ("RGBA", "P"):
        img_rgb = img.convert("RGB")
    else:
        img_rgb = img

    reco = recommendation["recommendation"]
    compressed_files = []

    # Redimensionner si recommandé
    if reco.get("redimensionner") and reco.get("nouvelle_resolution"):
        new_w = reco["nouvelle_resolution"]["width"]
        new_h = reco["nouvelle_resolution"]["height"]
        img_rgb = img_rgb.resize((new_w, new_h), Image.LANCZOS)

    # Priorité aux formats proposés par le LLM, puis ajout des formats manquants
    raw_formats = [reco.get("format_recommande")] + reco.get("formats_alternatifs", [])
    formats_to_compress = []

    for fmt in raw_formats:
        if not fmt:
            continue
        fmt = fmt.upper()
        if fmt not in formats_to_compress and fmt in SUPPORTED_FORMATS:
            formats_to_compress.append(fmt)

    for fmt in SUPPORTED_FORMATS:
        if fmt not in formats_to_compress:
            formats_to_compress.append(fmt)

    for fmt in formats_to_compress:
        ext = EXTENSIONS[fmt]
        output_filename = f"{path.stem}_compressed.{ext}"
        output_file = output_path / output_filename

        try:
            if fmt == "JPEG":
                quality = reco.get("qualite", 85)
                img_rgb.save(str(output_file), "JPEG", quality=quality, optimize=True)

            elif fmt == "PNG":
                compress_level = 9 if reco.get("niveau_compression") == "fort" else 6
                img_rgb.save(str(output_file), "PNG", compress_level=compress_level)

            elif fmt == "WEBP":
                quality = reco.get("qualite", 85)
                lossless = reco.get("sans_perte", False)
                img_rgb.save(str(output_file), "WEBP", quality=quality, lossless=lossless)

            elif fmt == "TIFF":
                img_rgb.save(str(output_file), "TIFF", compression="tiff_lzw")

            elif fmt == "JPEG2000":
                img_rgb.save(str(output_file), "JPEG2000")

            compressed_size = output_file.stat().st_size
            original_size = path.stat().st_size
            compression_ratio = round((1 - compressed_size / original_size) * 100, 2)

            compressed_files.append({
                "format": fmt,
                "path": str(output_file),
                "size_bytes": compressed_size,
                "size_kb": round(compressed_size / 1024, 2),
                "compression_ratio": compression_ratio,
                "success": True
            })

        except Exception as e:
            compressed_files.append({
                "format": fmt,
                "path": None,
                "error": str(e),
                "success": False
            })

    result = {
        "agent": "Agent4_Compressor",
        "image_path": image_path,
        "output_dir": str(output_path),
        "original_size_kb": round(path.stat().st_size / 1024, 2),
        "compressed_files": compressed_files
    }

    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python agent4_compressor.py '<image_path>' '<recommendation_json>'"
        }))
        sys.exit(1)

    img_path = sys.argv[1]
    reco = json.loads(sys.argv[2])
    result = compress_image(img_path, reco)
    print(json.dumps(result, indent=2, ensure_ascii=False))