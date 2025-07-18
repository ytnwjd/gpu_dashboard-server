from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict

from models import ApiResponse, GpuStatus, GpuStatusResponse
from services.gpu_service import gpu_service

router = APIRouter(
    prefix="/api/gpu",  
    tags=["GPU"],    
)

@router.get("/", response_model=GpuStatusResponse)
async def get_gpus():

    gpu_status_data = gpu_service.get_gpu()
    
    return GpuStatusResponse(
        code=200,
        message="GPU 상태 반환 성공",
        data=gpu_status_data 
    )