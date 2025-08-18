from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

def get_korean_time():
    return datetime.now(KST)

# Pydantic 모델 기본 설정
class MongoBaseModel(BaseModel):
    model_config = {
        "validate_by_name": True,
        "arbitrary_types_allowed": True
    }

# API 응답 모델
class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None

class Gpu(MongoBaseModel):
    id: int = Field(default=0, alias="_id")
    capacity: int
    isAvailable: bool = True

class Job(MongoBaseModel):
    id: int = Field(default=0, alias="_id")
    timestamp: datetime = Field(default_factory=get_korean_time)
    status: str = "pending"
    log: Optional[str] = None
    jobName: str
    projectPath: str
    venvPath: str
    mainFile: str
    gpuId: Optional[int] = None  # 배정된 GPU ID

class JobCreate(BaseModel):
    jobName: str
    projectPath: str
    venvPath: str
    mainFile: str

class JobResponse(ApiResponse):
    data: Optional[Job] = None

class JobListResponse(ApiResponse):
    data: Optional[List[Job]] = None
    
class JobQueue(MongoBaseModel):
    id: int = Field(default=0, alias="_id")
    queue: List[int] = [] 

class GpuStatus(BaseModel):
    gpu24gbActive: int  #사용 중인 GPU 개수
    gpu8gbActive: int
    gpu24gbAvailable: int   #사용 가능한 24gb gpu 갯수 
    gpu8gbAvailable: int
    jobsInQueue: int 
    totalGpu24gb: int = 6
    totalGpu8gb: int = 12    

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