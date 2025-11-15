from fastapi import APIRouter, HTTPException, Body, Query
from typing import List, Optional, Union
from pydantic import BaseModel

from models import ApiResponse, Job, JobListResponse, JobCreate, JobResponse, JobLogResponse
from services.job_service import job_service

class JobStatusUpdate(BaseModel):
    status: str

router = APIRouter(
    prefix="/user/{user_id}/jobs", 
    tags=["Jobs"],       # API 문서에서 그룹화할 태그
)


@router.get("/", 
            summary="ID로 Job 조회",
            description="특정 Job ID에 해당하는 Job의 상세 정보를 가져온다. job_id가 없으면 전체 목록을 반환한다.")
async def get_job_by_id(
    user_id: str,
    job_id: Optional[int] = Query(None, description="조회할 Job ID"),
    log: bool = Query(False, description="로그 조회 여부")
) -> Union[JobListResponse, JobResponse, JobLogResponse]:
    # job_id가 없으면 전체 목록 반환
    if job_id is None:
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
    
    # Job 정보 조회
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
        
        # log=true이면 로그 정보도 함께 조회
        if log:
            try:
                log_data = job_service.get_job_log(job_id)
                if log_data and log_data.get("code") == 200:
                    return JobResponse(
                        code=200,
                        message=f"Job {job_id}번 정보를 불러왔습니다.",
                        data=job,
                        log_content=log_data.get("log_content"),
                        file_name=log_data.get("file_name")
                    )
                else:
                    # 로그 조회 실패해도 job 정보는 반환
                    return JobResponse(
                        code=200,
                        message=f"Job {job_id}번 정보를 불러왔습니다. (로그 조회 실패)",
                        data=job,
                        log_content=None,
                        file_name=None
                    )
            except Exception as e:
                # 로그 조회 중 오류가 발생해도 job 정보는 반환
                return JobResponse(
                    code=200,
                    message=f"Job {job_id}번 정보를 불러왔습니다. (로그 조회 중 오류: {str(e)})",
                    data=job,
                    log_content=None,
                    file_name=None
                )
        else:   # log=false인 경우
            return JobResponse(
                code=200,
                message=f"Job {job_id}번 정보를 불러왔습니다.",
                data=job,
                log_content=None,
                file_name=None
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

@router.put("/", response_model=JobResponse,
            summary="Job 수정",
            description="특정 Job ID에 해당하는 Job을 수정")
async def update_job(
    user_id: str,
    job_id: int = Query(..., description="수정할 Job ID"),
    job_data: JobCreate = Body(...)
):
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


@router.delete("/", response_model=ApiResponse, summary="Job 삭제",
                description="특정 Job ID에 해당하는 Job을 삭제한다.")
async def delete_job(
    user_id: str,
    job_id: int = Query(..., description="삭제할 Job ID")
):
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