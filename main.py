from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from dotenv import load_dotenv
from api import jobs, gpu, file
from database import db
from database_init import initialize_database

load_dotenv() 
app = FastAPI(title="GPU Dashboard Server")

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

app.include_router(jobs.router)
app.include_router(gpu.router)
app.include_router(file.router)

@app.get("/")
def read_root():
    return {"message": "GPU Dashboard Server", "status": "running"}

@app.get("/health")
def health_check():
    try:
        # MongoDB 연결 상태 확인
        db.client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "message": "서버가 정상적으로 실행 중입니다."
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    initialize_database()

@app.on_event("shutdown")
async def shutdown_event():
    db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)