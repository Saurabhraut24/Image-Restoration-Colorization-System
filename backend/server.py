import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from utils import load_colorizer, colorize_image, restore_image

# Resolve absolute paths relative to this file
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR  = os.path.join(BASE_DIR, "..", "frontend")
TEMPLATE_DIR  = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR    = os.path.join(FRONTEND_DIR, "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)
CORS(app)

# Load model once at startup
net = load_colorizer()


@app.route("/")
def index():
    return send_from_directory(TEMPLATE_DIR, "index.html")


@app.route("/process", methods=["POST"])
def process_image():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file         = request.files["image"]
    restore_mode = request.form.get("restore", "true") == "true"
    color_mode   = request.form.get("color",   "true") == "true"

    # Read image
    img = Image.open(file.stream).convert("RGB")
    if max(img.size) > 1000:
        img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
    image_np = np.array(img)

    processed_image = image_np

    # Step 1: Restoration
    if restore_mode:
        processed_image = restore_image(processed_image)

    # Step 2: Colorization
    if color_mode:
        try:
            processed_image = colorize_image(processed_image, net)
        except Exception as e:
            return jsonify({"error": f"Colorization failed: {str(e)}"}), 500

    # Convert back to base64
    res_image = Image.fromarray(processed_image)
    buffered  = BytesIO()
    res_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return jsonify({"image": f"data:image/png;base64,{img_str}"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
