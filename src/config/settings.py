import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDCW3Pa05zL6oDAU2vMBz7fxJs6GL4I2bM")
# Claude OAuth — run: claude auth token  to get your token
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# Serper.dev — primary search provider (used by SerperDevTool or direct API)
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# --- Email SMTP ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

# --- Email IMAP ---
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))

# --- CrewAI LLM Config ---
CREWAI_DEFAULT_MODEL = os.getenv(
    "CREWAI_DEFAULT_MODEL", "gemini/gemini-2.5-flash"
)
CREWAI_PREMIUM_MODEL = os.getenv(
    "CREWAI_PREMIUM_MODEL", "anthropic/claude-sonnet-4-6"
)
CREWAI_CHEAP_MODEL = os.getenv(
    "CREWAI_CHEAP_MODEL", "anthropic/claude-haiku-4-5"
)

# --- Paths ---
DB_PATH = PROJECT_ROOT / "porcurment.db"
DATA_DIR = PROJECT_ROOT / "data"

# --- Search Defaults ---
MAX_SEARCH_RESULTS = 15
DEALS_TO_FIND = 10
TOP_DEALS_COUNT = 3
DEFAULT_REGION = "IL"
DEFAULT_CURRENCY = "ILS"
