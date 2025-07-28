from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api import jobs, gpu, file

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

app.include_router(jobs.router)
app.include_router(gpu.router)
app.include_router(file.router)

def read_root():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)