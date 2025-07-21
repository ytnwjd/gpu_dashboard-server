from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional

from models import ApiResponse, Job, JobListResponse, JobCreate, JobResponse
from services.job_service import job_service

router = APIRouter(
    prefix="/api/jobs",  # 이 라우터의 모든 경로에 "/api/jobs" 접두사 자동 적용
    tags=["Jobs"],       # API 문서에서 그룹화할 태그
)

@router.get("/", response_model=JobListResponse, 
            summary="모든 Job 목록 조회",
            description="모든 Job 목록을 최신순으로 가져온다.")
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

@router.get("/{job_id}", response_model=JobResponse, 
            summary="ID로 Job 조회",
            description="특정 Job ID에 해당하는 Job의 상세 정보를 가져온다.")
async def get_job_by_id(job_id: int):
    try:
        job = job_service.get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=404,
                detail=ApiResponse(
                    code=404,
                    message=f"Job ID {job_id}을(를) 찾을 수 없습니다.", 
                    data=None
                ).model_dump()
            )
        return JobResponse(
            code=200,
            message=f"Job {job_id}번 정보를 불러왔습니다.",
            data=job
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiResponse(
                code=500,
                message=f"Job {job_id}번 정보 불러오기를 실패했습니다.: {str(e)}",
                data=None
            ).model_dump()
        )

@router.post("/", response_model=ApiResponse, 
            summary="새로운 Job 생성",
            description="새로운 Job을 생성하고 등록한다.")
async def create_job(job_data: JobCreate = Body(...)):
    try:
        new_job = job_service.create_job(job_data)
        return ApiResponse(
            code=200,
            message="Job이 성공적으로 생성되었습니다.",
            data={"id": new_job.id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiResponse(
                code=500,
                message=f"Job 생성에 실패했습니다.: {str(e)}",
                data=None
            ).model_dump()
        )

@router.put("/{job_id}", response_model=ApiResponse,
            summary="Job 정보 수정",
            description="특정 Job ID에 해당하는 Job의 정보를 수정한다.")
async def update_job(job_id: int, job_data: JobCreate = Body(...)): 
    try:
        updated_job = job_service.update_job(job_id, job_data)
        if not updated_job:
            raise HTTPException(
                status_code=404,
                detail=ApiResponse(
                    code=404,
                    message=f"Job ID {job_id}을(를) 찾을 수 없습니다.",
                    data=None
                ).model_dump()
            )
        return ApiResponse(
            code=200,
            message=f"Job {job_id}번이 성공적으로 수정되었습니다.",
            data=None
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiResponse(
                code=500,
                message=f"Job {job_id}번 수정에 실패했습니다.: {str(e)}",
                data=None
            ).model_dump()
        )

@router.delete("/{job_id}", response_model=ApiResponse, summary="Job 삭제",
                description="특정 Job ID에 해당하는 Job을 삭제한다.")
async def delete_job(job_id: int):
    try:
        if not job_service.delete_job(job_id):
            raise HTTPException(
                status_code=404,
                detail=ApiResponse(
                    code=404,
                    message=f"Job을 찾을 수 없습니다.",
                    data=None
                ).model_dump()
            )
        return ApiResponse(
            code=200,
            message=f"Job이 성공적으로 삭제되었습니다.",
            data=None
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiResponse(
                code=500,
                message=f"Job 삭제에 실패했습니다.: {str(e)}",
                data=None
            ).model_dump()
        )