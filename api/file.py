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

user = "yusujeong"

def get_file_service() -> FileService:
    base_path = f"/Users/{user}"
    
    return FileService(base_remote_path=base_path) 

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
