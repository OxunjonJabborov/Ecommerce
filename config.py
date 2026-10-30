import os

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} muhit o'zgaruvchisi aniqlanmagan...")
    return value


DATABASE_URL = _require_env("DATABASE_URL")
SECRET_KEY = _require_env("SECRET_KEY")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")

UPLOAD_FOLDER = "uploads"
AVATAR_FOLDER = f"{UPLOAD_FOLDER}/avatars"
PRODUCT_FOLDER = f"{UPLOAD_FOLDER}/products"

os.makedirs(AVATAR_FOLDER, exist_ok=True)
os.makedirs(PRODUCT_FOLDER, exist_ok=True)
