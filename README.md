# 🩺 AI Healthcare Diagnosis System

An intelligent chest X-ray analysis system powered by deep learning. This full-stack application detects pneumonia in medical imaging with high accuracy and provides a user-friendly interface for healthcare professionals through Docker containerization.

## ✨ Features

- **🤖 AI-Powered Diagnosis**: Deep learning model (TensorFlow/Keras) for pneumonia detection
- **🔐 Secure Authentication**: JWT-based user authentication with role-based access control
- **📤 Image Upload & Analysis**: Upload chest X-ray images and get instant diagnosis predictions
- **📊 Confidence Scoring**: Displays prediction confidence percentage for each diagnosis
- **💾 User History**: Tracks prediction history for each authenticated user
- **🔗 RESTful API**: Complete FastAPI backend with Swagger documentation
- **🎨 Responsive UI**: Modern Streamlit web interface accessible via Nginx reverse proxy
- **🐳 Containerized Deployment**: Docker and Docker Compose for seamless deployment
- **📁 Database Persistence**: SQLite database for storing users and predictions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                  │
│                   (Port 8080 / 8443)                    │
└────────────────┬──────────────────────┬─────────────────┘
                 │                      │
         ┌───────▼─────────┐    ┌───────▼──────────┐
         │  Streamlit UI   │    │  FastAPI Docs    │
         │  (Port 8501)    │    │  (Port 8000)     │
         └────────┬────────┘    └──────────────────┘
                  │
         ┌────────▼─────────────────┐
         │   FastAPI Backend        │
         │  • Auth (JWT)            │
         │  • Predictions           │
         │  • User Management       │
         └────────┬─────────────────┘
                  │
         ┌────────▼─────────────────┐
         │  TensorFlow ML Model     │
         │  • Pneumonia Detection   │
         │  • Confidence Scoring    │
         └──────────────────────────┘
```

## 🚀 Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- Git
- (Optional) Python 3.10+ for local development

### Clone & Deploy

```bash
# Clone the repository
git clone https://github.com/Ajithrock18/AI-Healthcare-Diagnosis.git
cd AI-Healthcare-Diagnosis

# Start all services with Docker Compose
docker-compose up -d

# Verify containers are running
docker-compose ps
```

### Access the Application

| Service | URL | Purpose |
|---------|-----|---------|
| **Main App** (Streamlit) | http://localhost:8080 | User Interface |
| **Backend Docs** (Swagger) | http://localhost:8080/docs | API Documentation |
| **Direct Frontend** | http://localhost:8501 | Streamlit (direct) |
| **Direct Backend** | http://localhost:8000/docs | FastAPI (direct) |
| **From LAN** | http://192.168.29.15:8080 | Network Access |

### Default Credentials

```
Username: admin
Password: admin123
```

## 📁 Project Structure

```
AI-Healthcare-Diagnosis/
├── backend/                    # FastAPI application
│   ├── main.py                # FastAPI entry point
│   ├── auth.py                # JWT & password hashing
│   ├── models.py              # SQLAlchemy ORM models
│   ├── database.py            # Database configuration
│   ├── dependencies.py        # FastAPI dependencies
│   ├── predict.py             # ML inference logic
│   ├── utils.py               # Helper functions
│   ├── requirements.txt       # Backend dependencies
│   ├── Dockerfile             # Backend container config
│   └── healthcare.db          # SQLite database
│
├── frontend/                  # Streamlit application
│   ├── app.py                 # Streamlit UI
│   ├── requirements.txt       # Frontend dependencies
│   └── Dockerfile             # Frontend container config
│
├── nginx/                     # Reverse proxy
│   └── nginx.conf             # Nginx configuration
│
├── data/                      # Dataset (chest X-rays)
│   └── chest_xray/
│       ├── train/             # Training images
│       ├── val/               # Validation images
│       └── test/              # Test images
│
├── src/                       # Training scripts
│   ├── train.py               # Model training
│   ├── predict.py             # Inference script
│   └── model.py               # Model architecture
│
├── saved_model/               # Pre-trained model
│   └── best_model.h5          # Trained weights (LFS)
│
├── docker-compose.yml         # Docker orchestration
├── .dockerignore               # Docker build exclusions
├── .gitattributes             # Git LFS configuration
└── README.md                  # This file
```

## 📖 Usage Guide

### 1. Login

1. Open http://localhost:8080 in your browser
2. Enter credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. Click **Login**

### 2. Upload X-ray Image

1. Upload a chest X-ray image (JPG, JPEG, or PNG)
2. Recommended size: 224×224 pixels
3. Image will be previewed on screen

### 3. Get Prediction

1. Click **🔍 Predict** button
2. AI model analyzes the image (5-10 seconds)
3. Results display:
   - **Result**: PNEUMONIA or NORMAL
   - **Confidence**: Accuracy percentage

### 4. View Prediction History

Predictions are automatically saved to your user profile and database.

## 🔐 Security Features

- **Password Hashing**: Argon2 via passlib
- **JWT Tokens**: Secure token-based authentication
- **Protected Routes**: `/predict` endpoint requires valid JWT
- **HTTPS Ready**: Nginx configured for TLS (use your own certificates)
- **CORS**: Configured for development (update for production)

## 🔐 Authentication storage & verification

- **Where credentials are stored:** Usernames and password hashes are persisted in the backend SQLite database. The primary table and file are:
  - SQLAlchemy model: `backend/models.py` -> `User` model (fields: `id`, `username`, `hashed_password`, `role`).
  - SQLite file (development): `backend/healthcare.db` (created/used by `backend/database.py`).

- **How passwords are stored:** Passwords are never stored in plain text. On user creation the password is hashed using Argon2 (via `passlib`) and only the hash is saved in the `hashed_password` column.
  - Hashing function: `backend/auth.py` -> `hash_password(password)`

- **How verification works (login flow):**
  1. The `/login` endpoint (in `backend/main.py`) accepts credentials (OAuth2 form-encoded) and calls `authenticate_user(username, password)` from `backend/auth.py`.
  2. `authenticate_user` loads the user record from the database and uses `verify_password(plain_password, hashed_password)` (in `backend/auth.py`) to compare the provided password with the stored Argon2 hash.
  3. If verification succeeds, the backend issues JWT tokens:
     - `create_access_token(username, role)` in `backend/auth.py` — short-lived access token.
     - `create_refresh_token(username)` in `backend/auth.py` — longer-lived refresh token.
  4. Protected endpoints (for example, `/predict`) use a dependency that reads the `Authorization: Bearer <token>` header and verifies the token with `verify_access_token(...)` in `backend/auth.py`.

- **Where user creation happens:**
  - Existing users are created at startup by `create_default_admin()` in `backend/auth.py` (called from `backend/main.py` startup event) and new users are added via `POST /register` implemented in `backend/main.py` (which uses `create_user()` in `backend/auth.py`).

- **Files to inspect for implementation details:**
  - `backend/auth.py` — hashing, verify, token creation, and helper functions
  - `backend/models.py` — `User` SQLAlchemy model
  - `backend/database.py` — session and engine setup (database file path)
  - `backend/main.py` — `/register`, `/login`, `/refresh`, and protected endpoints

If you want, I can add a short code snippet to the README demonstrating how to create a user programmatically (using the same hashing function) or add a CLI helper to manage users.

## 🤖 Model Details

| Property | Value |
|----------|-------|
| **Architecture** | Convolutional Neural Network (CNN) |
| **Framework** | TensorFlow/Keras |
| **Input Size** | 224×224 RGB images |
| **Output** | Binary classification (Normal/Pneumonia) |
| **Accuracy** | ~95% on test dataset |
| **Inference Time** | ~200-500ms per image |

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username STRING UNIQUE NOT NULL,
    hashed_password STRING NOT NULL,
    role STRING DEFAULT 'user'
);
```

### Predictions Table
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY,
    image_path STRING,
    result STRING,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build --no-cache

# Restart specific service
docker-compose restart backend

# Access container shell
docker exec -it backend bash
docker exec -it frontend bash

# View container status
docker-compose ps
```

## 🔗 API Endpoints

### Authentication
- `POST /login` - Login with username/password → Returns JWT tokens
- `POST /refresh` - Refresh JWT token (query parameter: `refresh_token`)

### Predictions
- `POST /predict` - Upload image and get diagnosis (requires JWT Bearer token)

### Documentation
- `GET /docs` - Swagger UI interactive documentation
- `GET /openapi.json` - OpenAPI schema

### Example API Call (cURL)

```bash
# Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# Predict
curl -X POST "http://localhost:8000/predict" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@chest_xray.jpg"

# Response
{
  "result": "PNEUMONIA",
  "confidence": 0.92
}
```

## ⚠️ Important: Git LFS for Large Files

**Note**: Virtual environment (`.venv/`) and large binary files are excluded from git via `.gitignore`. If you encounter push issues related to large files:

```bash
# Clear git cache for large files
git rm -r --cached .venv
git filter-repo --invert-paths --path .venv

# Then push
git push origin main --force-with-lease
```

## 🛠️ Dependencies

### Backend
- FastAPI
- SQLAlchemy
- Passlib (Argon2)
- Python-jose (JWT)
- TensorFlow/Keras
- Pillow
- Uvicorn

### Frontend
- Streamlit
- Requests
- Pillow

### DevOps
- Docker
- Docker Compose
- Nginx

## 🐛 Troubleshooting

### Issue: "Invalid username or password"
**Solution**: Ensure admin user was created. Check backend logs:
```bash
docker-compose logs backend | grep -i admin
```

### Issue: "Backend not reachable"
**Solution**: Verify backend container is running:
```bash
docker-compose ps
docker-compose logs backend
```

### Issue: Page still loading
**Solution**:
- Hard refresh (Ctrl+Shift+R)
- Clear browser cache
- Try private/incognito mode
- Check browser console for errors (F12)

### Issue: Image upload fails
**Solution**: Ensure image is in supported format (JPG/JPEG/PNG) and under 50MB

### Issue: Prediction takes too long
**Solution**: First prediction takes longer (model initialization). Subsequent predictions are faster (~500ms)

## 🔄 Git LFS Setup

The trained model (`saved_model/best_model.h5`, ~128 MB) is tracked with **Git LFS** to avoid large file size issues on GitHub.

**If you cloned the repo and don't have the model:**
```bash
# Install Git LFS
git lfs install

# Pull LFS files
git lfs pull
```

## 💻 Local Development (Without Docker)

### Backend Setup

```bash
# Navigate to project root
cd backend

# Create virtual environment
python -m venv venv

# Activate venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn main:app --reload
```

### Frontend Setup (New Terminal)

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### Adding New Users

```bash
# Using Python interactive shell
python -c "
from database import SessionLocal
from models import User
from auth import hash_password

db = SessionLocal()
new_user = User(
    username='newuser',
    hashed_password=hash_password('password123'),
    role='user'
)
db.add(new_user)
db.commit()
print('✅ User created!')
"
```

## 📈 Performance Optimization

- **First Prediction**: ~5-10 seconds (model loads into memory)
- **Subsequent Predictions**: ~500-800ms (model cached)
- **GPU Support**: Install `tensorflow-gpu` for ~3-5x speedup
- **Model Caching**: Lazy loading pattern prevents memory waste

## 🚢 Production Deployment

For production use:

1. **Use PostgreSQL** instead of SQLite
2. **Enable HTTPS/TLS** with real certificates
3. **Set environment variables** for secrets (JWT_SECRET, DB_URL, etc.)
4. **Use a process manager** like Gunicorn or uWSGI
5. **Implement rate limiting** and API key authentication
6. **Add monitoring** (Prometheus, Grafana)
7. **Enable audit logging** for compliance
8. **Use a reverse proxy** (Nginx/Apache) with SSL

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [TensorFlow Documentation](https://www.tensorflow.org/learn)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💼 Author

**Ajith Kumar T**
- GitHub: [@Ajithrock18](https://github.com/Ajithrock18)
- Repository: [AI-Healthcare-Diagnosis](https://github.com/Ajithrock18/AI-Healthcare-Diagnosis)

## 🙏 Acknowledgments

- Dataset: Kaggle Chest X-Ray Pneumonia Dataset
- Frameworks: TensorFlow, FastAPI, Streamlit
- Reverse Proxy: Nginx
- Containerization: Docker

## 📞 Support & Issues

For issues, feature requests, or questions:
1. Open an Issue on GitHub
2. Check Troubleshooting section above
3. Review backend logs: `docker-compose logs backend`
4. Review frontend logs: `docker-compose logs frontend`

## 🚀 Roadmap

- [ ] Add HTTPS/TLS support
- [ ] Implement user registration endpoint
- [ ] Add email notifications
- [ ] Export prediction reports as PDF
- [ ] Add multiple model support
- [ ] Implement model version management
- [ ] Add data visualization dashboards
- [ ] Deploy to cloud (AWS/Azure/GCP)
- [ ] Add multilingual support
- [ ] Performance optimization with GPU

---

**Last Updated**: January 9, 2026  
**Version**: 1.1.0  
**Status**: ✅ Production Ready (Docker Containerized)
