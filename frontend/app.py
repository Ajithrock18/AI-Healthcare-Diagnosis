import streamlit as st
import requests
from PIL import Image
import io

# ---------------- URLs ----------------
LOGIN_URL = "http://127.0.0.1:8000/login"
PREDICT_URL = "http://127.0.0.1:8000/predict"

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="AI Healthcare Diagnosis",
    page_icon="🩺",
    layout="wide"
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
    padding: 40px;
    border-radius: 10px;
    text-align: center;
    font-size: 36px;
    font-weight: bold;
    letter-spacing: 1px;
}
.quote {
    font-style: italic;
    color: #cccccc;
    text-align: center;
    font-size: 20px;
    margin-bottom: 30px;
}
.card {
    background-color: #1a1a1a;
    border: 2px solid #ff0000;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-size: 18px;
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
header_img = Image.open("images/marvel_banner.jpg")
st.image(header_img, use_column_width=True)
st.markdown('<div class="header">🩺 AI-Driven Healthcare Diagnosis</div>', unsafe_allow_html=True)
st.markdown('<p class="quote">"Prevention is better than cure. Detect early, treat fast."</p>', unsafe_allow_html=True)

# ---------------- LOGIN ----------------
if st.session_state.access_token is None:
    st.subheader("🔑 Login to Continue")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username")
        with col2:
            password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                response = requests.post(LOGIN_URL, data={"username": username, "password": password})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.access_token = data["access_token"]
                    st.session_state.username = username
                    st.success(f"✅ Logged in as **{username}**")
                else:
                    st.error("❌ Invalid credentials")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Is FastAPI running?")
else:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")

    # ---------------- UPLOAD & PREDICT ----------------
    st.subheader("📤 Upload Chest X-ray")
    st.write("Supported formats: JPG, JPEG, PNG. Recommended size: 224x224 pixels.")

    uploaded_file = st.file_uploader("Choose an X-ray image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded X-ray", use_column_width=True)

        if st.button("🔍 Predict"):
            with st.spinner("Analyzing image..."):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="PNG")
                img_bytes.seek(0)

                files = {"file": ("image.png", img_bytes, "image/png")}
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

                try:
                    response = requests.post(PREDICT_URL, files=files, headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        result = data["result"]
                        confidence = data["confidence"]

                        if result.upper() == "PNEUMONIA":
                            st.markdown(
                                f'<div class="card" style="border-color:#ff3333;">'
                                f'<h2>🛑 Pneumonia Detected</h2>'
                                f'<p>Confidence: {confidence*100:.2f}%</p>'
                                f'</div>', unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f'<div class="card" style="border-color:#33cc33;">'
                                f'<h2>✅ Normal X-ray</h2>'
                                f'<p>Confidence: {confidence*100:.2f}%</p>'
                                f'</div>', unsafe_allow_html=True
                            )

                        st.progress(confidence if result.upper() == "PNEUMONIA" else 1 - confidence)

                    elif response.status_code == 401:
                        st.error("❌ Unauthorized. Please login again.")
                        st.session_state.access_token = None
                        st.session_state.username = None
                    else:
                        st.error(f"❌ Backend error: {response.status_code}\n{response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Is FastAPI running?")

# ---------------- TIPS SECTION ----------------
with st.container():
    st.write("---")
    st.subheader("💡 Tips for Better Diagnosis")
    col1, col2, col3 = st.columns(3)
    icons = ["icon1.png", "icon2.png", "icon3.png"]
    texts = [
        "Ensure clear X-ray images",
        "Follow the instructions for upload",
        "Consult a doctor for confirmed diagnosis"
    ]
    for col, icon, text in zip([col1, col2, col3], icons, texts):
        with col:
            img = Image.open(f"images/{icon}")
            st.image(img, width=80)
            st.markdown(f'<div class="card">{text}</div>', unsafe_allow_html=True)