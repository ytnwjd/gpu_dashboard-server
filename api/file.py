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

def get_file_service() -> FileService:  # FileService 의존성 주입
   
    return FileService(base_remote_path=os.path.expanduser("~/Documents/")) 

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

@router.get("/download-file", description="파일 다운로드")
async def download_file(
    path: str,
    file_service: FileService = Depends(get_file_service)
):
    try:
        file_content = await file_service.download_file(path)
        file_name = os.path.basename(path)  # 파일 이름을 추출하여 content-disposition 헤더에 사용
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=\"{file_name}\""}
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")