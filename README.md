# Système Intelligent de Compression d'Images
## Approche Multi-Agents et IA Générative

**Université Hassan II de Casablanca**  
**Faculté des Sciences & Techniques Mohammedia**  
**Module : Traitement d'Images**  
**Licence IRM**  
**Encadrant : Prof. Abdellah ADIB**  
**Année Universitaire : 2025-2026**

---

## Description

Ce projet implémente un système automatisé et intelligent de compression d'images
basé sur une architecture multi-agents et l'intégration d'un LLM (Gemini).

---

## Architecture Multi-Agents

Le système est composé de 6 agents autonomes :

| Agent | Rôle | Entrée | Sortie |
|-------|------|--------|--------|
| Agent 1 | Extracteur de caractéristiques | Image | JSON features |
| Agent 2 | Classificateur | JSON features | Type d'image |
| Agent 3 | Recommandeur LLM (Gemini) | Features + Type | Recommandations |
| Agent 4 | Compresseur | Image + Recommandations | Images compressées |
| Agent 5 | Évaluateur de qualité | Images | Métriques |
| Agent 6 | Générateur de rapport | Tous les résultats | Rapport JSON |

---

## Formats supportés

- JPEG
- PNG
- WebP
- TIFF
- JPEG2000

---

## Métriques de qualité

- **MSE** (Mean Squared Error)
- **PSNR** (Peak Signal-to-Noise Ratio)
- **SSIM** (Structural Similarity Index)
- **Taux de compression** (%)
- **Score qualité/taille combiné**

---

## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/ibniabdraman62-sketch/projet_compression.git
cd projet_compression
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les clés API

Crée un fichier `.env` à la racine :
```
GEMINI_API_KEY=votre_clé_gemini_ici
```

---

## Utilisation

### Traiter une seule image
```bash
python main.py dataset/photos/photo_01.jpg
```

### Traiter tout le dataset
```bash
python process_dataset.py dataset results
```

### Lancer l'interface Streamlit
```bash
python -m streamlit run app.py
```

---

## Structure du projet
```
projet_compression/
├── agents/
│   ├── __init__.py
│   ├── agent1_extractor.py
│   ├── agent2_classifier.py
│   ├── agent3_llm.py
│   ├── agent4_compressor.py
│   ├── agent5_evaluator.py
│   └── agent6_reporter.py
├── dataset/
│   ├── photos/
│   ├── documents/
│   ├── graphiques/
│   └── screenshots/
├── results/
├── .streamlit/
│   └── config.toml
├── main.py
├── process_dataset.py
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## Dataset

32 images réparties en 4 catégories :
- **Photos** : 9 images
- **Documents** : 7 images
- **Graphiques** : 8 images
- **Screenshots** : 8 images

---

## Dépendances principales
```
pillow
opencv-python
scikit-image
numpy
scipy
matplotlib
seaborn
anthropic
python-dotenv
tqdm
imageio
streamlit
google-genai
```

---

## Résultats

Les rapports JSON sont générés dans le dossier `results/` pour chaque image traitée.

---

## Auteurs

- **ABDRAMAN IBNI**  ABDRAMAN (Chef du projet)
- **ENNOURI** ZAKARIA
- **AMINE** ILHAM
- **RHALBI** SOUKAINA

---

## Licence

Projet académique — Université Hassan II de Casablanca 2025-2026
