import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DB_PATH = ROOT / "data" / "motor.db"
MODEL_PATH = ROOT / "models" / "motor_classifier.joblib"

S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_MODEL_KEY = "models/motor_classifier.joblib"
