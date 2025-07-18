from typing import List
from models import Job

job_list = [
        { "id": "6", 
        "timestamp": "2025-07-17 12:00:00", 
        "jobName": "NLP Model Training", 
        "logs": ["Log for job 6 line 1"], 
        "status": "대기",
        "projectPath": "/home/workspace",  
        "venvPath": "/home/workspace/.venv", 
        "mainFile": "/home/workspace/main.py"
        },
        {"id": "5", "timestamp": "2025-07-16 09:30:00", "jobName": "Image Classification", "status": "중단"},
        {"id": "4", "timestamp": "2025-07-15 11:00:00", "jobName": "Data Preprocessing", "status": "종료"},
        {"id": "3", "timestamp": "2025-07-15 10:15:30", "jobName": "Deep Learning Job C", "status": "종료"},
        {"id": "2", "timestamp": "2025-07-14 10:15:30", "jobName": "Deep Learning Model Training", "status": "종료"},
        {"id": "1", "timestamp": "2025-07-14 10:00:00", "jobName": "My first GPU job", "status": "종료"},  
]

class JobService:
    def get_all_jobs(self) -> List[Job]:
        # 실제로는 데이터베이스에서 Job 리스트를 조회
        return [Job(**job_data) for job_data in job_list]

# Service 인스턴스 생성 
job_service = JobService()