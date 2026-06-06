from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DB_PATH = ROOT / "data" / "motor.db"
MODEL_PATH = ROOT / "models" / "motor_classifier.joblib"
