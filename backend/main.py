from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import logging
import os

from database import engine, SessionLocal, Base
from models import Prediction, User
from utils import save_image
from predict import predict_image
from auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_password,
    SECRET_KEY,
    ALGORITHM,
)
from dependencies import get_current_user

# ---------------- ENV ----------------
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

# ---------------- APP ----------------
app = FastAPI(title="AI Healthcare Backend")

# ---------------- DATABASE ----------------
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup_event():
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
def login(form: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == form.username).first()
        if not user or not verify_password(form.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {
            "access_token": create_access_token(user.username, user.role),
            "refresh_token": create_refresh_token(user.username),
            "token_type": "bearer",
        }
    finally:
        db.close()

@app.post("/refresh")
def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        db = SessionLocal()
        user = db.query(User).filter(User.username == payload["sub"]).first()
        db.close()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {
            "access_token": create_access_token(user.username, user.role),
            "token_type": "bearer",
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# ---------------- PREDICT ----------------
@app.post("/predict")
def predict(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        image_path = save_image(file)
        result, confidence = predict_image(image_path)

        prediction = Prediction(
            user_id=current_user.id,
            image_path=image_path,
            result=result,
            confidence=confidence,
        )

        db.add(prediction)
        db.commit()

        return {
            "user": current_user.username,
            "result": result,
            "confidence": confidence,
        }

    except FileNotFoundError as e:
        logger.exception("Model file not found")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Internal Server Error")
