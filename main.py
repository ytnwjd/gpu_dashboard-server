from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS 
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 
    allow_headers=["*"],  # 모든 헤더 허용
)

def read_root():
    return {"message": "Hello, World!"}


@app.get("/api/jobs")
async def get_jobs():
    
    job_list = [
        {"id": "1", "timestamp": "2025-07-14 10:00:00", "jobName": "My first GPU job"},
        {"id": "2", "timestamp": "2025-07-14 10:15:30", "jobName": "Deep Learning Model Training"},
        {"id": "3", "timestamp": "2025-07-15 10:15:30", "jobName": "Deep Learning Job C"},
        {"id": "4", "timestamp": "2025-07-15 11:00:00", "jobName": "Data Preprocessing"},
        {"id": "5", "timestamp": "2025-07-16 09:30:00", "jobName": "Image Classification"},
        {"id": "6", "timestamp": "2025-07-17 12:00:00", "jobName": "NLP Model Training", "logs": ["Log for job 6 line 1", "Log for job 6 line 2", "Log for job 6 line 3", "Log for job 6 line 4"]},
    ]
    return job_list

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)