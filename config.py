"""
Provides various configuration and environment variables needed
"""
import os

from dotenv import load_dotenv

load_dotenv()

AVAILABLE_SCHEMAS = os.environ.get("AVAILABLE_SCHEMAS").replace(" ", "").split(",")

POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
PORT = os.environ.get("PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")

EMAIL_HOST = "smtp.gmail.com"  # Or your SMTP provider
EMAIL_PORT = 587
EMAIL_USER = "chinthahareeshkumarkhs@gmail.com"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECIPIENTS = [
    "cu.18bcs1449@gmail.com"
]

