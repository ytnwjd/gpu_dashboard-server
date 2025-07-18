from pydantic import BaseModel
from typing import List, Optional, Any

class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None # data 필드는 어떤 타입이든 될 수 있으므로 Any 사용

class Job(BaseModel):
    id: str
    timestamp: str
    jobName: str
    logs: Optional[List[str]] = None
    status: str
    projectPath: Optional[str] = None
    venvPath: Optional[str] = None
    mainFile: Optional[str] = None

class JobCreate(BaseModel):
    jobName: str
    projectPath: str
    venvPath: str
    mainFile: str

class JobListResponse(ApiResponse):
    data: Optional[List[Job]] = None