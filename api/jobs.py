from fastapi import APIRouter, HTTPException
from typing import List, Optional

from models import ApiResponse, Job, JobListResponse
from services.job_service import job_service

router = APIRouter(
    prefix="/api/jobs",  # 이 라우터의 모든 경로에 "/api/jobs" 접두사 자동 적용
    tags=["Jobs"],       # API 문서에서 그룹화할 태그
)

@router.get("/", response_model=JobListResponse) 
async def get_jobs():
    try:
        jobs = job_service.get_all_jobs()
        return JobListResponse(
            code=200,
            message="Job list를 불러왔습니다.",
            data=jobs
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiResponse(
                code=500,
                message=f"Job list 불러오기를 실패했습니다.: {str(e)}",
                data=None
            ).model_dump()
        )