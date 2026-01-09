from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from backend.database import engine, SessionLocal, Base
from backend.models import Prediction, User
from backend.utils import save_image
from backend.predict import predict_image
from backend.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_password,
    SECRET_KEY,
    ALGORITHM,
)
from backend.dependencies import get_current_user
from jose import jwt, JWTError
import logging
import os

# Suppress TensorFlow warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Healthcare Backend")
logger = logging.getLogger("backend")


# ---------------------- STARTUP: CREATE ADMIN ----------------------

def create_default_admin():
    with SessionLocal() as db:
        admin = db.query(User).filter(User.username == "admin").first()

        if not admin:
            admin = User(
                username="admin",
                hashed_password=hash_password("admin123"),  # ✅ fixed
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("✅ Admin created → username: admin | password: admin123")


create_default_admin()


# ---------------------- ROOT ----------------------

@app.get("/")
def root():
    return {"message": "AI Healthcare API running"}


# ---------------------- AUTH ----------------------

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == form.username).first()

    if not user or not verify_password(form.password, user.hashed_password):  # ✅ fixed
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": create_access_token(user.username, user.role),
        "refresh_token": create_refresh_token(user.username),
        "token_type": "bearer",
    }


@app.post("/refresh")
def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        with SessionLocal() as db:
            user = db.query(User).filter(User.username == payload["sub"]).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {
            "access_token": create_access_token(user.username, user.role),
            "token_type": "bearer",
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# ---------------------- PREDICT (PROTECTED) ----------------------

@app.post("/predict")
def predict(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    try:
        image_path = save_image(file)
        result, confidence = predict_image(image_path)

        with SessionLocal() as db:
            db.add(
                Prediction(
                    user_id=current_user.id,
                    image_path=image_path,
                    result=result,
                    confidence=confidence,
                )
            )
            db.commit()

        return {
            "user": current_user.username,
            "result": result,
            "confidence": confidence,
        }

    except FileNotFoundError as e:
        logger.exception("Model file not found")
        raise HTTPException(status_code=500, detail=str(e))

    except Exception:
        logger.exception("Unhandled error in /predict")
        raise HTTPException(status_code=500, detail="Internal Server Error")
