import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse

server_router = APIRouter()


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ========== 单文件上传 ==========
@server_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 生成唯一文件名，避免重名覆盖
    suffix = Path(file.filename).suffix
    save_name = f"{uuid.uuid4().hex}{suffix}"
    print(f"save_name: {save_name}")
    save_path = UPLOAD_DIR / save_name

    # 保存文件
    with save_path.open("wb") as buffer:
        buffer.write(await file.read())

    return {
        "filename": file.filename,
        "saved_as": save_name,
        "file_path": str(save_path)
    }



@server_router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        return {"error": "File not found"}

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
