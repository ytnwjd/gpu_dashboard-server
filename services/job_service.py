from typing import List, Dict, Optional
from datetime import datetime

from models import Job, JobCreate

_job_list: List[Dict] = [
    {
        "id": 6, 
        "timestamp": "2025-07-17 12:00:00",
        "jobName": "NLP Model Training",
        "logs": ["Log for job 6 line 1"],
        "status": "대기",
        "projectPath": "/home/workspace/nlp",
        "venvPath": "/home/workspace/nlp/.venv",
        "mainFile": "/home/workspace/nlp/train.py"
    },
    {
        "id": 5, 
        "timestamp": "2025-07-16 09:30:00",
        "jobName": "Image Classification",
        "logs": ["Log for job 5 line 1", "Log for job 5 line 2"],
        "status": "실행 중",
        "projectPath": "/home/workspace/image_clf",
        "venvPath": "/home/workspace/image_clf/.venv",
        "mainFile": "/home/workspace/image_clf/main.py"
    },
    {
        "id": 4,
        "timestamp": "2025-07-15 11:00:00",
        "jobName": "Data Preprocessing",
        "logs": [],
        "status": "종료",
        "projectPath": "/home/workspace/data_prep",
        "venvPath": "/home/workspace/data_prep/.venv",
        "mainFile": "/home/workspace/data_prep/process.py"
    },
    {
        "id": 3,
        "timestamp": "2025-07-15 10:15:30",
        "jobName": "Deep Learning Job C",
        "logs": [],
        "status": "종료",
        "projectPath": "/home/workspace/dl_c",
        "venvPath": "/home/workspace/dl_c/.venv",
        "mainFile": "/home/workspace/dl_c/run.py"
    },
    {
        "id": 2,
        "timestamp": "2025-07-14 10:15:30",
        "jobName": "Deep Learning Model Training",
        "logs": [],
        "status": "종료",
        "projectPath": "/home/workspace/dl_train",
        "venvPath": "/home/workspace/dl_train/.venv",
        "mainFile": "/home/workspace/dl_train/model.py"
    },
    {
        "id": 1,
        "timestamp": "2025-07-14 10:00:00",
        "jobName": "My first GPU job",
        "logs": [],
        "status": "종료",
        "projectPath": "/home/workspace/my_job",
        "venvPath": "/home/workspace/my_job/.venv",
        "mainFile": "/home/workspace/my_job/start.py"
    },
]

class JobService:
    def get_all_jobs(self) -> List[Job]:
        return [Job(**job_data) for job_data in _job_list]

    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        for job_data in _job_list:
            if job_data["id"] == job_id:
                return Job(**job_data)
        return None

    def create_job(self, job_data: JobCreate) -> Job:
        new_job_dict = job_data.model_dump()
        
        max_id = 0
        if _job_list:
            max_id = max(job["id"] for job in _job_list)
        new_job_dict["id"] = max_id + 1 
        
        new_job_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_job_dict["logs"] = []
        new_job_dict["status"] = "대기"
        _job_list.insert(0, new_job_dict)
        return Job(**new_job_dict)

    def update_job(self, job_id: int, job_data: JobCreate) -> Optional[Job]:
        for i, job_dict in enumerate(_job_list):
            if job_dict["id"] == job_id:
                updated_data = job_data.model_dump()
                _job_list[i].update(updated_data)
                _job_list[i]["status"] = "대기"
                return Job(**_job_list[i])
        return None

    def delete_job(self, job_id: int) -> bool: 
        global _job_list
        initial_len = len(_job_list)
        _job_list = [job for job in _job_list if job["id"] != job_id]
        return len(_job_list) < initial_len

job_service = JobService()