from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import io, os

from services.file_service import FileService 
from models import DirectoryContent

router = APIRouter(
    prefix="/api/files",  
    tags=["files"],       
)

def get_file_service() -> FileService:
    REMOTE_HOST = os.getenv("REMOTE_HOST")
    REMOTE_USERNAME = os.getenv("REMOTE_USERNAME")
    REMOTE_PORT_STR = os.getenv("REMOTE_PORT")
    SSH_KEY_FILE = os.getenv("SSH_KEY_FILE")
    SSH_KEY_PASSWORD = os.getenv("SSH_KEY_PASSWORD")
    
    try:
        REMOTE_PORT = int(REMOTE_PORT_STR)
    except ValueError:
        raise ValueError("REMOTE_PORT 환경 변수가 유효한 숫자가 아닙니다.")
    
    BASE_REMOTE_PATH = f"/home/{REMOTE_USERNAME}"

    return FileService(
        hostname=REMOTE_HOST,
        username=REMOTE_USERNAME,
        port=REMOTE_PORT,
        key_filename=SSH_KEY_FILE,
        password=SSH_KEY_PASSWORD,
        base_remote_path=BASE_REMOTE_PATH
    )

@router.get("/list-contents", response_model=DirectoryContent, description="특정 경로에 있는 파일 및 폴더 목록을 조회")
async def list_contents(
    path: Optional[str] = "",
    file_service: FileService = Depends(get_file_service) 
):
    try:
        return await file_service.list_directory_contents(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

# @router.get("/download-file", description="파일 다운로드")
# async def download_file(
#     path: str,
#     file_service: FileService = Depends(get_file_service)
# ):
#     try:
#         file_content = await file_service.download_file(path)
#         file_name = path.split('/')[-1] # 파일명만 추출
        
#         return StreamingResponse(
#             io.BytesIO(file_content),
#             media_type="application/octet-stream",
#             headers={"Content-Disposition": f"attachment; filename=\"{file_name}\""}
#         )
#     except FileNotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except IOError as e:
#         raise HTTPException(status_code=500, detail=f"Server error: {e}")