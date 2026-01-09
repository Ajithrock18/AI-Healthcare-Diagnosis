import os
import tensorflow as tf
import numpy as np
from PIL import Image

_MODEL = None
_MODEL_PATH = os.path.join("saved_model", "best_model.h5")


def _load_model():
    global _MODEL
    if _MODEL is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {_MODEL_PATH}")
        _MODEL = tf.keras.models.load_model(_MODEL_PATH)
    return _MODEL


def predict_image(image_path):
    model = _load_model()
    image = Image.open(image_path).convert("RGB").resize((224, 224))
    img = np.array(image) / 255.0
    img = np.expand_dims(img, axis=0)

    prediction = float(model.predict(img)[0][0])

    # model uses sigmoid output: prediction ~ probability of positive class
    if prediction >= 0.5:
        return "PNEUMONIA", prediction
    else:
        return "NORMAL", 1.0 - prediction
