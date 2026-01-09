# AI Healthcare Diagnosis System

An AI-powered chest X-ray diagnostic platform with FastAPI backend, Streamlit frontend, and TensorFlow CNN model for binary classification (NORMAL vs PNEUMONIA).

## 🏗️ Project Architecture

```
AI-Healthcare-Diagnosis/
├── backend/                    # FastAPI server (port 8000)
│   ├── main.py                # FastAPI app, auth endpoints, /predict
│   ├── models.py              # SQLAlchemy ORM models (User, Prediction)
│   ├── database.py            # SQLite setup, sessionmaker
│   ├── auth.py                # JWT auth, password hashing (werkzeug)
│   ├── dependencies.py        # FastAPI Depends: get_current_user
│   ├── predict.py             # CNN inference (lazy model loading)
│   └── utils.py               # Image upload handling
│
├── frontend/                   # Streamlit UI (port 8501)
│   ├── app.py                 # Login, image upload, prediction display
│   └── images/                # UI assets (banners, icons)
│
├── src/                        # Training utilities (CLI scripts)
│   ├── model.py               # CNN architecture (create_model)
│   ├── train.py               # Training script with ImageDataGenerator, checkpoints
│   ├── predict.py             # Single-image inference (CLI)
│   └── __init__.py
│
├── data/                       # Dataset (not in repo)
│   └── chest_xray/
│       ├── train/NORMAL/, train/PNEUMONIA/
│       ├── val/NORMAL/, val/PNEUMONIA/
│       └── test/NORMAL/, test/PNEUMONIA/
│
├── saved_model/
│   └── best_model.h5          # Trained CNN (Git LFS)
│
├── notebooks/                  # Jupyter exploratory analysis
│   └── medical-dataset.ipynb
│
├── uploads/                    # Temp uploaded images (auto-created)
│   └── images/
│
├── requirements.txt            # All dependencies
├── .gitignore                  # Exclude venv, *.h5 (LFS tracked)
├── .gitattributes             # Git LFS config (*.h5)
├── healthcare.db              # SQLite database (auto-created)
└── README.md
```

## 🚀 Quick Start

### 1. Environment Setup

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Start Backend (FastAPI)

In **Terminal 1**:
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Note:** On first run, the backend creates:
- SQLite database (`healthcare.db`)
- Admin user: `username: admin | password: admin123`
- Uploads directory: `uploads/images/`

### 3. Start Frontend (Streamlit)

In **Terminal 2** (separate window from backend):
```powershell
cd .\frontend
streamlit run app.py
```

Streamlit opens at `http://localhost:8501`

### 4. Login & Use

1. **Login** with: `admin / admin123`
2. **Upload** a chest X-ray image (JPG/PNG)
3. **Get prediction**: NORMAL or PNEUMONIA with confidence score
4. **View history**: Predictions stored in database

---

## 🧠 Model Training (Optional)

To retrain the CNN on your own dataset:

```powershell
# From project root
python .\src\train.py \
  --data-dir ".\data\chest_xray" \
  --image-size 224 \
  --batch-size 32 \
  --epochs 10 \
  --save-model ".\saved_model\best_model.h5"
```

**Flags:**
- `--data-dir`: Path to dataset root (must contain `train/`, `val/`, `test/` subdirs)
- `--image-size`: Input image size (default 224×224)
- `--batch-size`: Training batch size (default 32)
- `--epochs`: Number of epochs (default 10)
- `--save-model`: Output model path (default `src/best_model.h5`)

**Dataset structure expected:**
```
data/chest_xray/
├── train/NORMAL/*.jpg
├── train/PNEUMONIA/*.jpg
├── val/NORMAL/*.jpg
├── val/PNEUMONIA/*.jpg
├── test/NORMAL/*.jpg
└── test/PNEUMONIA/*.jpg
```

---

## 🔐 Backend API Endpoints

**Base URL:** `http://127.0.0.1:8000`

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/docs` | GET | - | FastAPI Swagger UI (interactive API) |
| `/login` | POST | - | Login (returns JWT access_token) |
| `/predict` | POST | Bearer | Upload image, return prediction |
| `/history` | GET | Bearer | User's prediction history |

**Example: Predict (cURL)**
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@./chest_xray.jpg"
```

**Response:**
```json
{
  "result": "PNEUMONIA",
  "confidence": 0.92,
  "created_at": "2026-01-09T10:30:00"
}
```

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | FastAPI | ≥2.0 |
| **Server** | Uvicorn | ≥0.24 |
| **Frontend** | Streamlit | ≥1.20 |
| **ML Model** | TensorFlow/Keras | ≥2.11 |
| **Database** | SQLite/SQLAlchemy | - |
| **Auth** | JWT + Werkzeug | - |
| **File Storage** | Local (uploads/) + Git LFS | - |

---

## 📋 Troubleshooting

### Backend won't start
- **Error:** `ModuleNotFoundError: No module named 'fastapi'`
  - **Fix:** Ensure venv is activated and `pip install -r requirements.txt` completed.

- **Error:** `FileNotFoundError: Model file not found: saved_model/best_model.h5`
  - **Fix:** Ensure LFS-tracked model file exists. If using Git LFS:
    ```powershell
    git lfs pull
    ```

### Frontend won't connect to backend
- **Error:** `Cannot connect to backend. Is FastAPI running?`
  - **Fix:** Start backend first (Terminal 1), wait for "Uvicorn running" message, then start frontend.
  - **Check:** Visit `http://127.0.0.1:8000/docs` — should show Swagger UI.

### Model inference slow
- **Tip:** First prediction takes longer (model loads). Subsequent predictions are faster.
- **GPU:** Install `tensorflow-gpu` if CUDA/cuDNN available for faster inference.

### Database locked
- **Error:** `database is locked`
  - **Fix:** Delete `healthcare.db` and restart backend (creates fresh DB).

---

## 🔄 Git LFS Setup (Large Model Files)

The trained model (`saved_model/best_model.h5`, ~128 MB) is tracked with **Git LFS** to avoid large file size issues on GitHub.

**If you cloned the repo and don't have the model:**
```powershell
# Install Git LFS
git lfs install

# Pull LFS files
git lfs pull
```

---

## 📈 Performance & Accuracy

- **Architecture:** Simple CNN (4 Conv layers + Dropout)
- **Input:** 224×224 RGB chest X-ray
- **Output:** Binary classification (sigmoid) + confidence score
- **Database:** Stores all predictions with timestamps for analytics

**Note:** This is a demonstration model. For clinical use:
- Train on validated, clinical datasets (DICOM images).
- Implement regulatory compliance (HIPAA, FDA 21 CFR Part 11).
- Use ensemble models or validated pre-trained networks.
- Include radiologist review workflows.

---

## 📝 Development Notes

- **Auth:** JWT tokens valid for 30 minutes. Refresh logic in `backend/auth.py`.
- **Image Upload:** Timestamped filenames prevent collisions; temp files in `uploads/images/`.
- **Model Prediction:** Lazy loading (`_MODEL` global cache) avoids reloading on every request.
- **Logging:** Configure in `backend/main.py` to write to file for production.
- **Database:** SQLite suitable for development. For production, use PostgreSQL.

---

## 🤝 Contributing

Feel free to:
- Train models on larger/better datasets
- Add more endpoints (user management, audit logs, batch predictions)
- Improve frontend UI/UX
- Add unit tests and CI/CD

---

## 📄 License & Disclaimer

**This is a demonstration project for educational purposes only.**

- Not intended for clinical diagnosis without proper validation.
- Use trained models responsibly and always under expert supervision.
- See NHS/FDA guidelines for actual medical AI deployment.

---

**Last Updated:** January 9, 2026
**Repository:** https://github.com/Ajithrock18/AI-Healthcare-Diagnosis.git
