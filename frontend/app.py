import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image

# Load trained model
model = tf.keras.models.load_model("saved_model/best_model.h5")

# Page title
st.set_page_config(page_title="AI Healthcare Diagnosis", layout="centered")

st.title("🩺 AI-Driven Healthcare Diagnosis System")
st.write("Upload a Chest X-ray image to detect Pneumonia")

# Image upload
uploaded_file = st.file_uploader("Choose an X-ray image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded X-ray", use_container_width=True)

    # Preprocessing
    image = image.resize((224, 224))
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Prediction
    prediction = model.predict(img_array)[0][0]

    # Output
    if prediction > 0.5:
        st.error(f"🛑 Pneumonia Detected (Confidence: {prediction:.2f})")
    else:
        st.success(f"✅ Normal X-ray (Confidence: {1 - prediction:.2f})")
