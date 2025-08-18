from typing import List, Optional

from database import db
from models import JobQueue

class JobQueueService:
    def _create_queue(self) -> JobQueue:       
        try:
            queue_collection = db.get_collection('job_queue')
            new_queue = JobQueue(queue=[])
            result = queue_collection.insert_one(new_queue.model_dump())
            
            new_queue.id = result.inserted_id
            return new_queue
            
        except Exception as e:
            # print(f"대기열 생성 실패: {e}")
            return JobQueue(queue=[])

    def add_to_queue(self, job_id: int) -> bool:   
        try:
            queue_collection = db.get_collection('job_queue')
            
            queue_data = queue_collection.find_one()
            if not queue_data:
                self._create_queue()
                queue_data = queue_collection.find_one()
               
            if job_id in queue_data.get('queue', []):
                # print(f"작업 {job_id}는 이미 대기열에 있습니다.")
                return True
            
            result = queue_collection.update_one(
                {"_id": queue_data["_id"]},
                {"$push": {"queue": job_id}}
            )
            
            if result.modified_count > 0:
                # print(f"작업 {job_id}를 대기열에 추가했습니다.")
                return True
            else:
                # print(f"작업 {job_id} 대기열 추가 실패")
                return False
                
        except Exception as e:
            print(f"대기열 추가 실패: {e}")
            return False

    def remove_from_queue(self, job_id: int) -> bool:
        try:
            queue_collection = db.get_collection('job_queue')
            queue_data = queue_collection.find_one()
            
            if not queue_data:
                return True
            
            result = queue_collection.update_one(
                {"_id": queue_data["_id"]},
                {"$pull": {"queue": job_id}}
            )
            
            if result.modified_count > 0:
                # print(f"작업 {job_id}를 대기열에서 제거했습니다.")
                return True
            else:
                # print(f"작업 {job_id} 대기열 제거 실패")
                return False
                
        except Exception as e:
            print(f"대기열 제거 실패: {e}")
            return False

    def get_next_job(self) -> Optional[int]:
        try:
            queue_collection = db.get_collection('job_queue')
            queue_data = queue_collection.find_one()
            
            if not queue_data or not queue_data.get('queue'):
                return None
                       
            next_job_id = queue_data['queue'][0]
            return next_job_id
            
        except Exception as e:
            print(f"다음 작업 조회 실패: {e}")
            return None

    def get_queue_length(self) -> int:        
        try:
            queue_collection = db.get_collection('job_queue')
            queue_data = queue_collection.find_one()
            
            if not queue_data:
                return 0
            
            return len(queue_data.get('queue', []))
            
        except Exception as e:
            print(f"대기열 길이 조회 실패: {e}")
            return 0

job_queue_service = JobQueueService() 