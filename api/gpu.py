from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models import ApiResponse, GpuStatus, GpuStatusResponse, Gpu
from services.gpu_service import gpu_service

router = APIRouter(
    prefix="/api/gpu",  
    tags=["GPU"],    
)

@router.get("/", response_model=GpuStatusResponse)
async def get_gpus():
    try:
        gpu_status_data = gpu_service.get_gpu_status()
        
        return GpuStatusResponse(
            code=200,
            message="GPU 상태 반환 성공",
            data=gpu_status_data 
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiResponse(
                code=500,
                message=f"GPU 상태 조회 실패: {str(e)}",
                data=None
            ).model_dump()
        )