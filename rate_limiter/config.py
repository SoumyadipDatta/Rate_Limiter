
import os

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ratelimiter_db")
LIMIT = int(os.getenv("RATE_LIMIT", "5"))                # max requests per window
WINDOW_SECONDS = int(os.getenv("WINDOW_SECONDS", "60"))   # window length
FAIL_OPEN = os.getenv("FAIL_OPEN", "true").lower() == "true"  # allow traffic if DB is down
PORT = int(os.getenv("PORT", "5000"))
