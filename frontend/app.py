import streamlit as st
import requests
from PIL import Image
import io
import os

# URLs for Docker
LOGIN_URL = "http://backend:8000/login"
PREDICT_URL = "http://backend:8000/predict"

st.set_page_config(page_title="AI Healthcare Diagnosis", page_icon="🩺", layout="centered")

# ---------------- Session State ----------------
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

# ---------------- Styles ----------------
st.markdown("""
<style>
body { background-color: #0d0d0d; color: white; }
.card { background:#1a1a1a; border:2px solid #ff0000; padding:15px; border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# ---------------- Banner ----------------
banner = "images/marvel_banner.jpg"
if os.path.exists(banner):
    st.image(banner, use_column_width=True)
else:
    st.title("🩺 AI Healthcare Diagnosis")

# ---------------- Login ----------------
if not st.session_state.access_token:
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            r = requests.post(LOGIN_URL, json={"username": username, "password": password}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                st.session_state.access_token = data["access_token"]
                st.session_state.username = username
                st.session_state.role = data["role"]
                st.success(f"Login successful ✅ Role: {st.session_state.role}")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        except requests.exceptions.RequestException:
            st.error("❌ Backend not reachable")

# ---------------- Prediction ----------------
else:
    st.sidebar.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")
    uploaded = st.file_uploader("Upload Chest X-ray", type=["jpg", "jpeg", "png"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, width=300)
        if st.button("🔍 Predict"):
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            buf.seek(0)
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            try:
                r = requests.post(PREDICT_URL, files={"file": ("xray.png", buf, "image/png")}, headers=headers, timeout=20)
                if r.status_code == 200:
                    data = r.json()
                    st.success(f"🧠 Result: **{data['result']}**  \n📊 Confidence: **{data['confidence']*100:.2f}%**")
                else:
                    st.error(f"❌ Prediction failed: {r.text}")
            except requests.exceptions.RequestException:
                st.error("❌ Prediction service unavailable")
