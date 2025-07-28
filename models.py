from pydantic import BaseModel
from typing import List, Optional, Any

class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None # data 필드는 어떤 타입이든 될 수 있으므로 Any 사용

class Job(BaseModel):
    id: int
    timestamp: str
    status: str
    logs: Optional[List[str]] = None
    jobName: str
    projectPath: Optional[str] = None
    venvPath: Optional[str] = None
    mainFile: Optional[str] = None

class JobCreate(BaseModel):
    jobName: str
    projectPath: str
    venvPath: str
    mainFile: str

class JobResponse(ApiResponse):
    data: Optional[Job] = None

class JobListResponse(ApiResponse):
    data: Optional[List[Job]] = None

class GpuStatus(BaseModel):
    gpu24gbActive: int  #사용 중인 GPU 개수
    gpu8gbActive: int
    gpu24gbAvailable: int   #사용 가능한 24gb gpu 갯수 
    gpu8gbAvailable: int
    jobsInQueue: int 

class GpuStatusResponse(ApiResponse):
    data: Optional[GpuStatus] = None
    
class FileItem(BaseModel):  #파일 또는 폴더의 기본 정보
    name: str
    is_directory: bool
    path: str
    size: Optional[int] = None  # 파일인 경우에만 크기 정보
    last_modified: Optional[float] = None # (timestamp)

class DirectoryContent(BaseModel):
    current_path: str
    items: List[FileItem]    