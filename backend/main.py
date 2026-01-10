# backend/main.py

import os
import logging
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from database import engine, SessionLocal, Base
from models import User, Prediction
from utils import save_image
from predict import predict_image
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM,
    verify_access_token,
    authenticate_user,
)
# ---------------- ENV ----------------
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

# ---------------- APP ----------------
app = FastAPI(title="AI Healthcare Backend")

# ---------------- DATABASE ----------------
Base.metadata.create_all(bind=engine)

# ---------------- DEPENDENCIES ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    """
    Dependency to get the current user from Bearer token
    """
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        username = verify_access_token(token)
        if not username:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")

# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup_event():
    """
    Create default admin user if not exists
    """
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            logger.info("✅ Default admin created (admin/admin123)")
    finally:
        db.close()

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"message": "AI Healthcare API running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# ---------------- AUTH ----------------
@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "access_token": create_access_token(user.username, user.role),
        "refresh_token": create_refresh_token(user.username),
        "token_type": "bearer",
    }

@app.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using a refresh token
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = db.query(User).filter(User.username == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return {
            "access_token": create_access_token(user.username, user.role),
            "token_type": "bearer",
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# ---------------- PREDICTION ----------------
@app.post("/predict")
def predict(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Make prediction on uploaded image
    """
    try:
        # Save image
        image_path = save_image(file)
        # Get prediction and confidence
        result, confidence = predict_image(image_path)
        # Save to DB
        prediction = Prediction(
            user_id=current_user.id,
            image_path=image_path,
            result=result,
            confidence=confidence,
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return {
            "user": current_user.username,
            "result": result,
            "confidence": confidence,
            "created_at": prediction.created_at,
        }

    except FileNotFoundError as e:
        logger.exception("Model file not found")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ---------------- EXAMPLE PROTECTED ENDPOINT ----------------
@app.get("/profile")
def profile(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "role": current_user.role,
        "total_predictions": len(current_user.predictions),
    }
