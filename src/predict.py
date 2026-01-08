import os
import sys
import argparse
import numpy as np
from tensorflow.keras.preprocessing import image

# ensure `src` package directory is on path when running from project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def load_model_from_path(model_path):
    from tensorflow.keras.models import load_model

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return load_model(model_path)


def predict_image(img_path: str, model, image_size: int = 224, labels=None):
    img = image.load_img(img_path, target_size=(image_size, image_size))
    x = image.img_to_array(img) / 255.0
    x = np.expand_dims(x, axis=0)
    prob = float(model.predict(x)[0][0])
    # For binary sigmoid: prob is probability of class '1'
    if labels is None:
        labels = ["NORMAL", "PNEUMONIA"]
    # choose label for probability threshold 0.5
    pred_idx = 1 if prob >= 0.5 else 0
    return {"label": labels[pred_idx], "probability": prob}


def parse_args():
    p = argparse.ArgumentParser(description="Predict chest X-ray class for an image")
    p.add_argument("image", help="Path to image file to predict")
    p.add_argument("--model", required=True, help="Path to trained Keras .h5 model")
    p.add_argument("--image-size", type=int, default=224)
    return p.parse_args()


def main():
    args = parse_args()
    model = load_model_from_path(args.model)
    result = predict_image(args.image, model, image_size=args.image_size)
    print(f"Predicted: {result['label']} (prob={result['probability']:.4f})")


if __name__ == "__main__":
    main()