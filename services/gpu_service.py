from typing import List
from models import GpuStatus, GpuStatusResponse

TOTAL_GPU_24GB = 6
TOTAL_GPU_8GB = 12

class GpuService:
    def get_gpu(self) -> GpuStatus:
        
        active_24gb = 5
        active_8gb = 4

        # 사용 가능한 GPU 개수 계산
        available_24gb = TOTAL_GPU_24GB - active_24gb
        available_8gb = TOTAL_GPU_8GB - active_8gb
        jobs_in_queue = 0   #전체 대기열 중에서 대기 중인 job 개수

        gpu_status = {
            "gpu24gbActive": active_24gb,
            "gpu8gbActive": active_8gb,
            "gpu24gbAvailable": available_24gb,
            "gpu8gbAvailable": available_8gb,
            "jobs_in_queue": jobs_in_queue,
        }
        
        return GpuStatus(**gpu_status)
        
gpu_service = GpuService()