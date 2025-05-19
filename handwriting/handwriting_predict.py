"""
Character recognition powered by machine learning from CaptainDario (DaAppLab)
https://github.com/CaptainDario/DaKanji-Single-Kanji-Recognition/tree/master
"""

import numpy as np
import tensorflow as tf
from PIL import Image
import os

# Load the model
model = tf.saved_model.load(os.path.join(os.path.dirname(__file__), 'tf'))
infer = model.signatures["serving_default"]
labels = None

with open(os.path.join(os.path.dirname(__file__), "labels_fixed.txt"), encoding='utf-8') as f:
    labels = [line.strip() for line in f]

def preprocess_image(img_path):
    img = Image.open(img_path).convert('L')  # Grayscale
    img = img.resize((64, 64))
    img_arr = np.array(img).astype(np.float32) / 255.0  # Normalize to [0,1]
    img_arr = img_arr[np.newaxis, ..., np.newaxis]      # Shape: (1, 64, 64, 1)
    return img_arr

def predict_image(img_path):
    img_arr = preprocess_image(img_path)
    output = infer(tf.constant(img_arr))
    probs = list(output.values())[0].numpy()[0]
    pred_idx = np.argmax(probs)
    pred_char = labels[pred_idx]
    print(f"Predicted character: {pred_char}")
    return pred_char
