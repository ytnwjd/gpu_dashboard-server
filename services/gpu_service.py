from typing import List, Optional
from bson import ObjectId

from database import db
from models import Gpu, GpuStatus

class GpuService:
    def get_gpu_status(self) -> GpuStatus:
        try:
            gpus_collection = db.get_collection('gpus')
            
            # 24GB GPU 통계
            active_24gb = gpus_collection.count_documents({"capacity": 24, "isAvailable": False})
            available_24gb = gpus_collection.count_documents({"capacity": 24, "isAvailable": True})
            
            # 8GB GPU 통계
            active_8gb = gpus_collection.count_documents({"capacity": 8, "isAvailable": False})
            available_8gb = gpus_collection.count_documents({"capacity": 8, "isAvailable": True})
            
            # 대기열 길이 조회 (pending 상태인 작업 수)
            jobs_collection = db.get_collection('jobs')
            jobs_in_queue = jobs_collection.count_documents({"status": "pending"})
            
            gpu_status = {
                "gpu24gbActive": active_24gb,
                "gpu8gbActive": active_8gb,
                "gpu24gbAvailable": available_24gb,
                "gpu8gbAvailable": available_8gb,
                "jobsInQueue": jobs_in_queue,
            }
            
            return GpuStatus(**gpu_status)
            
        except Exception as e:
            print(f"GPU 상태 조회 실패: {e}")
            
            return GpuStatus(
                gpu24gbActive=0,
                gpu8gbActive=0,
                gpu24gbAvailable=6,
                gpu8gbAvailable=12,
                jobsInQueue=0,
            )

gpu_service = GpuService()