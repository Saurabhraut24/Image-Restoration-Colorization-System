import cv2
import numpy as np
import os
import requests
from PIL import Image

# Paths for the models (relative to this file's location)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
PROTOTXT = os.path.join(MODEL_DIR, "colorization_deploy_v2.prototxt")
MODEL    = os.path.join(MODEL_DIR, "colorization_release_v2.caffemodel")
POINTS   = os.path.join(MODEL_DIR, "pts_in_hull.npy")

# URLs for downloading models
URL_PROTOTXT = "https://storage.openvinotoolkit.org/repositories/datumaro/models/colorization/colorization_deploy_v2.prototxt"
URL_MODEL    = "https://storage.openvinotoolkit.org/repositories/datumaro/models/colorization/colorization_release_v2.caffemodel"
URL_POINTS   = "https://storage.openvinotoolkit.org/repositories/datumaro/models/colorization/pts_in_hull.npy"


def download_file(url, filename):
    """Downloads a file from a URL to a local path."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if os.path.exists(filename):
        return

    print(f"Downloading {filename} from {url}...")
    response = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Downloaded {filename}")


def setup_models():
    """Ensures all model files are present."""
    download_file(URL_PROTOTXT, PROTOTXT)
    download_file(URL_MODEL, MODEL)
    download_file(URL_POINTS, POINTS)


def load_colorizer():
    """Loads the pre-trained colorization model."""
    setup_models()

    # Load the model
    net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)

    # Load the cluster centers
    pts = np.load(POINTS)

    # Add the cluster centers as 1x1 convolutions to the model
    class8 = net.getLayerId("class8_ab")
    conv8  = net.getLayerId("conv8_313_rh")
    pts    = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs  = [np.full([1, 313], 2.606, dtype="float32")]

    return net


def colorize_image(image_np, net):
    """Colorizes a grayscale image."""
    # Convert image to Lab color space
    scaled = image_np.astype("float32") / 255.0
    lab    = cv2.cvtColor(scaled, cv2.COLOR_RGB2Lab)

    # Resize L channel to 224x224 (model input size)
    resized = cv2.resize(lab, (224, 224))
    l = cv2.split(resized)[0]
    l -= 50  # Mean centering

    # Run the model
    net.setInput(cv2.dnn.blobFromImage(l))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

    # Resize predicted ab channels to original size
    ab = cv2.resize(ab, (image_np.shape[1], image_np.shape[0]))

    # Combine original L channel with predicted ab channels
    l_orig    = cv2.split(lab)[0]
    colorized = np.concatenate((l_orig[:, :, np.newaxis], ab), axis=2)

    # Convert back to RGB
    colorized = cv2.cvtColor(colorized, cv2.COLOR_Lab2RGB)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")

    return colorized


def restore_image(image_np):
    """Applies optimised denoising and sharpening to modernise the image."""
    # 1. Subtle Denoising (reduced strength to avoid oil-painting effect)
    denoised = cv2.fastNlMeansDenoisingColored(image_np, None, 6, 6, 7, 21)

    # 2. Better Sharpening (kernel-based approach blended for natural look)
    kernel        = np.array([[-1, -1, -1],
                               [-1,  9, -1],
                               [-1, -1, -1]])
    sharpened_raw = cv2.filter2D(denoised, -1, kernel)
    sharpened     = cv2.addWeighted(denoised, 0.7, sharpened_raw, 0.3, 0)

    # 3. Controlled Contrast adjustment (CLAHE)
    lab = cv2.cvtColor(sharpened, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl    = clahe.apply(l)
    limg  = cv2.merge((cl, a, b))
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)

    return final
