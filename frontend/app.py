import streamlit as st
import requests
from PIL import Image
import io
import os

# ---------------- URLs (DOCKER FIXED) ----------------
# When running under Docker Compose, route auth via nginx so the frontend
# can post to `/login` at the root. Use the nginx service name on the
# Docker network so the Streamlit server (container) can reach the proxy.
LOGIN_URL = "http://nginx/login"
PREDICT_URL = "http://backend:8000/predict"

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="AI Healthcare Diagnosis",
    page_icon="🩺",
    layout="centered"
)

# ---------------- Session State ----------------
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "username" not in st.session_state:
    st.session_state.username = None

# ---------------- CSS STYLING ----------------
st.markdown("""
<style>
body {
    background-color: #0d0d0d;
    color: #f0f0f0;
    font-family: 'Segoe UI', sans-serif;
}
.header {
    background: linear-gradient(to right, #ff0000, #990000);
    color: white;
    padding: 25px;
    border-radius: 10px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    letter-spacing: 1px;
    margin-bottom: 10px;
}
.quote {
    font-style: italic;
    color: #cccccc;
    text-align: center;
    font-size: 16px;
    margin-bottom: 20px;
}
.card {
    background-color: #1a1a1a;
    border: 2px solid #ff0000;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-size: 16px;
    margin-top: 10px;
}
.card:hover {
    transform: scale(1.02);
    transition: 0.3s ease-in-out;
    box-shadow: 0 0 10px #ff0000;
}
.login-section {
    background-color: #262626;
    padding: 20px;
    border-radius: 10px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
banner_path = "images/marvel_banner.jpg"
if os.path.exists(banner_path):
    st.image(Image.open(banner_path), width=600)
else:
    st.markdown('<div class="header">🩺 AI-Driven Healthcare Diagnosis</div>', unsafe_allow_html=True)

st.markdown(
    '<p class="quote">"Prevention is better than cure. Detect early, treat fast."</p>',
    unsafe_allow_html=True
)

# ---------------- LOGIN ----------------
if st.session_state.access_token is None:
    st.subheader("🔑 Login to Continue")

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username")
    with col2:
        password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            response = requests.post(
                LOGIN_URL,
                data={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.access_token = data["access_token"]
                st.session_state.username = username
                st.success(f"✅ Logged in as **{username}**")
            else:
                st.error("❌ Invalid credentials")
        except requests.exceptions.RequestException:
            st.error("❌ Cannot connect to backend")
else:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")

    # ---------------- UPLOAD & PREDICT ----------------
    st.subheader("📤 Upload Chest X-ray")
    st.write("Supported formats: JPG, JPEG, PNG (224×224 recommended)")

    uploaded_file = st.file_uploader(
        "Choose an X-ray image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded X-ray", width=400)

        if st.button("🔍 Predict"):
            with st.spinner("Analyzing image..."):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="PNG")
                img_bytes.seek(0)

                files = {"file": ("image.png", img_bytes, "image/png")}
                headers = {
                    "Authorization": f"Bearer {st.session_state.access_token}"
                }

                try:
                    response = requests.post(
                        PREDICT_URL,
                        files=files,
                        headers=headers,
                        timeout=10
                    )

                    if response.status_code == 200:
                        data = response.json()
                        result = data["result"]
                        confidence = data["confidence"]

                        if result.upper() == "PNEUMONIA":
                            st.markdown(
                                f"""
                                <div class="card" style="border-color:#ff3333;">
                                    <h2>🛑 Pneumonia Detected</h2>
                                    <p>Confidence: {confidence*100:.2f}%</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.progress(confidence)
                        else:
                            st.markdown(
                                f"""
                                <div class="card" style="border-color:#33cc33;">
                                    <h2>✅ Normal X-ray</h2>
                                    <p>Confidence: {(1-confidence)*100:.2f}%</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.progress(1 - confidence)

                    elif response.status_code == 401:
                        st.error("❌ Session expired. Login again.")
                        st.session_state.access_token = None
                        st.session_state.username = None
                    else:
                        st.error(response.text)

                except requests.exceptions.RequestException:
                    st.error("❌ Backend connection failed")

# ---------------- TIPS SECTION ----------------
st.write("---")
st.subheader("💡 Tips for Better Diagnosis")

col1, col2, col3 = st.columns(3)
tips = [
    "Ensure clear X-ray images",
    "Follow the instructions for upload",
    "Consult a doctor for confirmed diagnosis"
]

for col, text in zip([col1, col2, col3], tips):
    with col:
        st.markdown(f'<div class="card">{text}</div>', unsafe_allow_html=True)
