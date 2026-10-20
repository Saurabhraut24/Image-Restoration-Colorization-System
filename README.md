---
title: Image Restoration & Colorization System
emoji: 🎨
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
license: mit
---

# 🎨 AI Image Restoration & Colorization System

Restore your old black and white memories into high-quality, modern colored images using Deep Learning.

## Features
- **Modern Restoration** – Removes noise and sharpens old, blurry photos.
- **AI Colorization** – Predicts realistic colors using a pre-trained Deep Learning model (Caffe).
- **Flask Web App** – A beautiful, responsive web interface (HTML5 + CSS3 + JS).
- **Streamlit App** – Quick interactive demo in a browser tab.
- **Jupyter Notebook** – Step-by-step walkthrough of the AI logic.

---

## Project Structure

```
Ip project/
├── backend/                    # Flask server & core AI logic
│   ├── server.py               # Flask entry point  (python backend/server.py)
│   └── utils.py                # Image processing & model utilities
│
├── frontend/                   # Web UI served by Flask
│   ├── templates/
│   │   └── index.html          # Main HTML page
│   └── static/
│       ├── css/style.css       # Glassmorphism UI styles
│       └── js/script.js        # Drag-and-drop + API calls
│
├── models/                     # AI model weights (auto-downloaded on first run)
│   ├── colorization_deploy_v2.prototxt
│   ├── colorization_release_v2.caffemodel
│   └── pts_in_hull.npy
│
├── notebooks/                  # Jupyter demo
│   └── restoration_demo.ipynb
│
├── samples/                    # Sample images for demo
│   ├── B2DBy.jpg               # Example B&W input
│   └── restored_photo.png      # Example colorized output
│
├── streamlit_app/              # Streamlit alternative UI
│   └── app.py                  # streamlit run streamlit_app/app.py
│
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

---

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Flask Web Application
```bash
python backend/server.py
```
Open your browser at → **http://127.0.0.1:5000**

### 3. Run the Streamlit App
```bash
streamlit run streamlit_app/app.py
```

### 4. Explore the Notebook
Open `notebooks/restoration_demo.ipynb` in VS Code or Jupyter to walk through the processing logic step-by-step.

> **Note**: Model weights (`models/*.caffemodel`) are downloaded automatically on the first run. The file is ~123 MB.

---

## Technologies Used

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| AI / CV | OpenCV DNN, Caffe colorization model |
| Frontend | HTML5, CSS3 (Glassmorphism), Vanilla JS |
| Alt UI | Streamlit |
| Data | NumPy, Pillow |
