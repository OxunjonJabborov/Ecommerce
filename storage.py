import shutil

from fastapi import UploadFile


def save_upload(file: UploadFile, folder: str, name: str) -> str:
    """Faylni folder ichiga saqlaydi va uning URL manzilini qaytaradi."""
    filename = file.filename or ""
    extension = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    path = f"{folder}/{name}.{extension}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/{path}"
