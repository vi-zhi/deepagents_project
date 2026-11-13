import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI", "postgresql://postgres:123456@127.0.0.1:5432/deepagents")

SANDBOX_IMAGE = os.getenv(
    "SANDBOX_IMAGE",
    "sandbox-registry.cn-zhangjiakou.cr.aliyuncs.com/opensandbox/code-interpreter:v1.0.1",
)
SANDBOX_IDLE_TIMEOUT = 10 * 60
SANDBOX_CLEANUP_INTERVAL = 60

PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_SKILLS_DIR = PROJECT_ROOT / "skills"
PPT_SKILL_DIR = LOCAL_SKILLS_DIR / "vizhi-pptx-generator"
PPT_CORE_DEPS = ["python-pptx"]

MODEL_NAME = "deepseek:deepseek-v4-flash"
