import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI", "")

SANDBOX_IMAGE = os.getenv(
    "SANDBOX_IMAGE",
    "",
)
SANDBOX_IDLE_TIMEOUT = 10 * 60
SANDBOX_CLEANUP_INTERVAL = 60

PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_SKILLS_DIR = PROJECT_ROOT / "skills"
PPT_SKILL_DIR = LOCAL_SKILLS_DIR / "vizhi-pptx-generator"
PPT_CORE_DEPS = ["python-pptx"]

MODEL_NAME = ""

MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", ""))
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "")
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")
MYSQL_POOL_MIN = int(os.getenv("MYSQL_POOL_MIN", "2"))
MYSQL_POOL_MAX = int(os.getenv("MYSQL_POOL_MAX", "8"))
MYSQL_CONNECT_TIMEOUT = int(os.getenv("MYSQL_CONNECT_TIMEOUT", "10"))
MYSQL_READ_TIMEOUT = int(os.getenv("MYSQL_READ_TIMEOUT", "30"))