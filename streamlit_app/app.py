import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import sys
import time

# Ensure backend/ is importable from streamlit_app/
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "..", "backend")
SAMPLES_DIR = os.path.join(BASE_DIR, "..", "samples")
MODELS_DIR  = os.path.join(BASE_DIR, "..", "models")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from utils import load_colorizer, colorize_image, restore_image  # noqa: E402

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Image Restoration & Colorization",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4CAF50, #8BC34A);
    }
    .upload-text {
        font-size: 1.2rem;
        font-weight: 600;
        color: #f0f2f6;
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    .stMarkdown p {
        color: #bcc0c4;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    st.info(
        "This tool restores old black & white photos by reducing noise, "
        "enhancing sharpness, and adding realistic colors."
    )

    restore_mode = st.checkbox("Apply Modern Restoration (Denoise & Sharpen)", value=True)
    color_mode   = st.checkbox("Apply Colorization", value=True)

    st.divider()
    st.write("### Model Status")
    caffe_model = os.path.join(MODELS_DIR, "colorization_release_v2.caffemodel")
    if os.path.exists(caffe_model):
        st.success("✅ Model Ready for Processing")
    else:
        st.warning("⚠️ Model Weights: Missing (Will download on start)")

# --- MAIN CONTENT ---
st.title("🎨 Image Restoration & Colorization")
st.subheader("Transform old memories into modern masterpieces")

uploaded_file = st.file_uploader("Choose an old photo...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Load and display original image
    image    = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Original Photo")
        st.image(image, use_container_width=True)

    if st.button("✨ Restore Image"):
        with st.spinner("🚀 AI is working its magic..."):
            progress_bar = st.progress(0)

            # Step 1: Restoration
            if restore_mode:
                st.write("Step 1: Removing noise and enhancing details...")
                processed_image = restore_image(image_np)
                progress_bar.progress(40)
            else:
                processed_image = image_np

            # Step 2: Colorization
            if color_mode:
                st.write("Step 2: Predicting colors using Deep Learning...")
                try:
                    net             = load_colorizer()
                    processed_image = colorize_image(processed_image, net)
                    progress_bar.progress(90)
                except Exception as e:
                    st.error(f"Error during colorization: {e}")
                    progress_bar.progress(100)

            progress_bar.progress(100)
            time.sleep(0.5)

            with col2:
                st.write("### Restored Photo")
                res_image = Image.fromarray(processed_image)
                st.image(res_image, use_container_width=True)

                # Download button
                img_bytes = cv2.imencode(
                    ".png", cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR)
                )[1].tobytes()
                st.download_button(
                    label="📥 Download Restored Image",
                    data=img_bytes,
                    file_name="restored_photo.png",
                    mime="image/png"
                )

            st.success("✅ Done! Your memory has been restored.")
            st.balloons()

else:
    st.info("👆 Please upload a photo to get started.")

    # Sample images from samples/ folder
    st.divider()
    st.write("### Example: Original B&W → Colorized Result")
    ex_col1, ex_col2, ex_col3 = st.columns(3)

    sample_bw      = os.path.join(SAMPLES_DIR, "B2DBy.jpg")
    sample_colored = os.path.join(SAMPLES_DIR, "restored_photo.png")

    with ex_col1:
        st.write("Original B&W")
        if os.path.exists(sample_bw):
            st.image(sample_bw, caption="Historical Photo", use_container_width=True)

    with ex_col2:
        st.write("Colorized")
        if os.path.exists(sample_colored):
            st.image(sample_colored, caption="Colorized Result", use_container_width=True)

    with ex_col3:
        st.write("Features")
        st.markdown("""
        - **Denoising**: Removes scan artifacts.
        - **Sharpening**: Brings back textures.
        - **Colorization**: Vivid, realistic hues.
        """)

st.markdown("---")
