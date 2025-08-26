from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta

from database import db
from models import Job, JobCreate
from database_init import get_next_job_id

KST = timezone(timedelta(hours=9))

def get_korean_time():
    return datetime.now(KST)

class JobService:
    def get_all_jobs(self) -> List[Job]:
        try:
            jobs_collection = db.get_collection('jobs')
            jobs_data = jobs_collection.find().sort("requested_at", -1)
            
            self._check_and_release_completed_jobs()
            jobs_data = jobs_collection.find().sort("requested_at", -1)
            
            jobs = []
            for job_data in jobs_data:               
                job_dict = dict(job_data)
                jobs.append(Job(**job_dict))
            return jobs
        except Exception as e:
            print(f"작업 목록 조회 실패: {e}")
            return []

    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        try:
            self._check_and_release_completed_jobs()
            
            jobs_collection = db.get_collection('jobs')
            job_data = jobs_collection.find_one({"_id": job_id})
            if job_data:
                job_dict = dict(job_data)
                return Job(**job_dict)
            return None
        except Exception as e:
            print(f"작업 조회 실패: {e}")
            return None

    def _assign_available_gpu(self) -> Optional[int]:
        try:
            gpus_collection = db.get_collection('gpus')
            
            available_24gb = gpus_collection.find_one({
                "capacity": 24,
                "isAvailable": True
            })
            
            if available_24gb:
                gpu_id = available_24gb["_id"]
                
                gpus_collection.update_one(
                    {"_id": gpu_id},
                    {"$set": {"isAvailable": False}}
                )
                # print(f"24GB GPU {gpu_id} 배정 완료")
                return gpu_id
            
            available_8gb = gpus_collection.find_one({
                "capacity": 8,
                "isAvailable": True
            })
            
            if available_8gb:
                gpu_id = available_8gb["_id"]            
                gpus_collection.update_one(
                    {"_id": gpu_id},
                    {"$set": {"isAvailable": False}}
                )
                # print(f"8GB GPU {gpu_id} 배정 완료")
                return gpu_id
            
            #print("사용 가능한 GPU가 없습니다.\n 대기열에 추가하시겠습니까?")
            return None
            
        except Exception as e:
            print(f"GPU 배정 실패: {e}")
            return None

    def _check_and_release_completed_jobs(self):
        try:
            jobs_collection = db.get_collection('jobs')
            gpus_collection = db.get_collection('gpus')
            
            # completed나 failed 상태이면서 GPU가 배정된 작업들 찾기
            completed_jobs = jobs_collection.find({
                "status": {"$in": ["completed", "failed"]},
                "gpuId": {"$ne": None}
            })
            
            released_gpus = []
            
            for job in completed_jobs:
                job_id = job["_id"]
                gpu_id = job["gpuId"]
                
                # GPU를 사용 가능 상태로 변경
                gpus_collection.update_one(
                    {"_id": gpu_id},
                    {"$set": {"isAvailable": True}}
                )
                
                # 작업에서 GPU ID 제거
                jobs_collection.update_one(
                    {"_id": job_id},
                    {"$unset": {"gpuId": ""}}
                )
                
                released_gpus.append(gpu_id)
                print(f"🔄 Job ID {job_id}의 GPU {gpu_id}를 해제했습니다.")
            
            # GPU가 해제되었다면 대기 중인 작업에 자동 할당
            if released_gpus:            
                self._process_queued_jobs()
            
        except Exception as e:
            print(f"완료된 작업 GPU 해제 중 오류 발생: {e}")

    def _process_queued_jobs(self):       
        try:
            # 대기 중인 작업 중에서 요청 시간이 가장 빠른 작업을 찾기
            jobs_collection = db.get_collection('jobs')
            oldest_pending_job = jobs_collection.find_one(
                {"status": "pending"},
                sort=[("requested_at", 1)]  # 요청 시간 오름차순 (가장 빠른 것부터)
            )
            
            if not oldest_pending_job:
                return
            
            next_job_id = oldest_pending_job["_id"]
            assigned_gpu_id = self._assign_available_gpu()
            if not assigned_gpu_id:
                return
            
            # 작업에 GPU 배정하고 상태를 running으로 변경
            result = jobs_collection.update_one(
                {"_id": next_job_id},
                {"$set": {
                    "gpuId": assigned_gpu_id, 
                    "status": "running",
                    "started_at": get_korean_time().isoformat()  # 작업 시작 시간 기록
                }}
            )
            
            if result.modified_count > 0:
                print(f"🚀 대기 작업 {next_job_id}에 GPU {assigned_gpu_id} 배정 완료")
            
        except Exception as e:
            print(f"대기열 작업 처리 실패: {e}")

    def create_job(self, job_data: JobCreate) -> Optional[Job]:
        try:
            jobs_collection = db.get_collection('jobs')
            
            assigned_gpu_id = self._assign_available_gpu()
                    
            job_id = get_next_job_id()
            if job_id is None:
                # print("Job ID 생성 실패")
                return None
            
            new_job_dict = job_data.model_dump()
            new_job_dict["_id"] = job_id
            new_job_dict["status"] = "pending"
            new_job_dict["log"] = None
            new_job_dict["requested_at"] = get_korean_time().isoformat()  # 작업 요청 시간 기록
            
            # user 필드가 없으면 기본값 설정
            if not new_job_dict.get("user"):
                new_job_dict["user"] = "anonymous"
            
            if assigned_gpu_id:
                # GPU가 있으면 바로 배정
                new_job_dict["gpuId"] = assigned_gpu_id
                new_job_dict["status"] = "running"
                new_job_dict["started_at"] = get_korean_time().isoformat()  # 작업 시작 시간 기록
            else:
                # GPU가 없으면 대기열에 추가
                new_job_dict["gpuId"] = None
            
            result = jobs_collection.insert_one(new_job_dict)
            created_job = jobs_collection.find_one({"_id": job_id})
            
            if created_job:             
                job_dict = dict(created_job)
                return Job(**job_dict)
            return None
            
        except Exception as e:
            print(f"작업 생성 실패: {e}")
            return None

    def update_job(self, job_id: int, job_data: JobCreate) -> Optional[Job]:
        try:
            jobs_collection = db.get_collection('jobs')
            
            update_data = job_data.model_dump()
            
            result = jobs_collection.update_one(
                {"_id": job_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated_job = jobs_collection.find_one({"_id": job_id})
                if updated_job:
                    job_dict = dict(updated_job)
                    return Job(**job_dict)
            return None
            
        except Exception as e:
            print(f"작업 업데이트 실패: {e}")
            return None

    def delete_job(self, job_id: int) -> bool:
        try:
            jobs_collection = db.get_collection('jobs')
            
            job_data = jobs_collection.find_one({"_id": job_id})
            if job_data and job_data.get("gpuId"):
                gpu_id = job_data["gpuId"]
                gpus_collection = db.get_collection('gpus')
                gpus_collection.update_one(
                    {"_id": gpu_id},
                    {"$set": {"isAvailable": True}}
                )                
                
                self._process_queued_jobs()
            
            result = jobs_collection.delete_one({"_id": job_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"작업 삭제 실패: {e}")
            return False

    def inspect_job(self, job_candidate: JobCreate) -> Optional[str]:
        empty_fields = []

        if not job_candidate.jobName or job_candidate.jobName.strip() == "":
            empty_fields.append("Job 이름")

        if job_candidate.projectPath is None or job_candidate.projectPath.strip() == "":
            empty_fields.append("프로젝트 경로")

        if job_candidate.venvPath is None or job_candidate.venvPath.strip() == "":
            empty_fields.append("가상 환경 경로")

        if job_candidate.mainFile is None or job_candidate.mainFile.strip() == "":
            empty_fields.append("메인 파일 경로")

        if empty_fields:
            if len(empty_fields) == 1:
                return f"{empty_fields[0]}은(는) 비어 있을 수 없습니다."
            elif len(empty_fields) == 2:
                return f"{empty_fields[0]}와 {empty_fields[1]}는 비어 있을 수 없습니다."
            else:
                return f"{', '.join(empty_fields[:-1])}와 {empty_fields[-1]}는 비어 있을 수 없습니다."
        else:
            return None

job_service = JobService()