import os

UPLOAD_FOLDER = "uploads"
AVATAR_FOLDER = f"{UPLOAD_FOLDER}/avatars"
PRODUCT_FOLDER = f"{UPLOAD_FOLDER}/products"

os.makedirs(AVATAR_FOLDER, exist_ok=True)
os.makedirs(PRODUCT_FOLDER, exist_ok=True)
