from fastapi import APIRouter, HTTPException, Body, Query
from typing import List, Optional
from pydantic import BaseModel

from models import ApiResponse, Job, JobListResponse, JobCreate, JobResponse, JobLogResponse
from services.job_service import job_service

class JobStatusUpdate(BaseModel):
    status: str

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

@router.post("/", response_model=JobResponse, 
            summary="새로운 Job 생성",
            description="새로운 Job을 생성하고 사용 가능한 GPU를 자동으로 배정")
async def create_job(job_data: JobCreate = Body(...)):
    try:
        validation_message = job_service.inspect_job(job_data)

        if validation_message:
            raise HTTPException(
                status_code=400,
                detail=ApiResponse(
                    code=400,
                    message=f"Job 데이터 검증 실패: {validation_message}",
                    data=None
                ).model_dump()
            )
        
        new_job = job_service.create_job(job_data)
        
        if not new_job:
            raise HTTPException(
                status_code=500,
                detail=ApiResponse(
                    code=500,
                    message="Job 생성에 실패했습니다.",
                    data=None
                ).model_dump()
            )

        if new_job.gpuId:
            message = f"Job이 성공적으로 생성되었습니다. (GPU {new_job.gpuId} 배정됨)"
        else:
            message = f"Job이 대기열에 추가되었습니다."

        return JobResponse(
            code=200,
            message=message,
            data=new_job
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiResponse(
                code=500,
                message=f"Job 생성에 실패했습니다.: {str(e)}",
                data=None
            ).model_dump()
        )

@router.put("/{job_id}", response_model=JobResponse,
            summary="Job 수정",
            description="특정 Job ID에 해당하는 Job을 수정")
async def update_job(job_id: int, job_data: JobCreate = Body(...)):
    try:
        validation_message = job_service.inspect_job(job_data)

        if validation_message:
            raise HTTPException(
                status_code=400,
                detail=ApiResponse(
                    code=400,
                    message=f"Job 데이터 검증 실패: {validation_message}",
                    data=None
                ).model_dump()
            )
        
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

        return JobResponse(
            code=200,
            message="Job이 성공적으로 수정되었습니다.",
            data=updated_job
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiResponse(
                code=500,
                message=f"Job 수정에 실패했습니다.: {str(e)}",
                data=None
            ).model_dump()
        )

@router.get("/{job_id}/log", response_model=JobLogResponse, 
            summary="Job 로그 조회",
            description="Job ID에 해당하는 Job의 로그 파일 반환")
async def get_job_log(job_id: int):
    try:
        log_data = job_service.get_job_log(job_id)
        
        if not log_data:
            raise HTTPException(
                status_code=404,
                detail=JobLogResponse(
                    code=404,
                    message=f"Job ID {job_id}을(를) 찾을 수 없습니다.",
                    log_content=None,
                    file_name=None
                ).model_dump()
            )
        
        return JobLogResponse(
            code=log_data["code"],
            message=log_data["message"],
            log_content=log_data["log_content"],
            file_name=log_data["file_name"]
        )
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=JobLogResponse(
                code=500,
                message=f"Job 로그 조회에 실패했습니다.: {str(e)}",
                log_content=None,
                file_name=None
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