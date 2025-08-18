import sys
import os
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from database import db

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_collections():
    print("📁 MongoDB 컬렉션 생성 중...")
    collections = ['gpus', 'jobs', 'job_queue', 'counters'] # counters(Job ID를 자동 증가)
    
    for collection_name in collections:
        try:
            collection = db.get_collection(collection_name)
            # print(f"{collection_name} 컬렉션 생성 완료")
        except Exception as e:
            print(f"{collection_name} 컬렉션 생성 실패: {e}")

def create_indexes():
    print("MongoDB 인덱스 생성 중...")
    
    try:        
        jobs_collection = db.get_collection('jobs')
        jobs_collection.create_index([("timestamp", DESCENDING)])
        jobs_collection.create_index("status")
        # print("jobs 컬렉션 인덱스 생성 완료")
    except Exception as e:
        print(f"jobs 컬렉션 인덱스 생성 실패: {e}")
    
    try:
        gpus_collection = db.get_collection('gpus')
        gpus_collection.create_index("isAvailable")
        # print("gpus 컬렉션 인덱스 생성 완료")
    except Exception as e:
        print(f"gpus 컬렉션 인덱스 생성 실패: {e}")

def create_initial_gpus():
    try:
        gpus_collection = db.get_collection('gpus')
        
        if gpus_collection.count_documents({}) > 0:            
            return
                
        for i in range(1, 7):
            gpu_data = {
                "_id": i,
                "capacity": 24,
                "isAvailable": True
            }
            gpus_collection.insert_one(gpu_data)
                
        for i in range(7, 19):
            gpu_data = {
                "_id": i,
                "capacity": 8,
                "isAvailable": True
            }
            gpus_collection.insert_one(gpu_data)    
        
    except Exception as e:
        print(f"GPU 데이터 생성 실패: {e}")

def create_initial_counters():
    try:
        counters_collection = db.get_collection('counters')
        jobs_collection = db.get_collection('jobs')
        
        max_job_id = 0
        if jobs_collection.count_documents({}) > 0:
            max_job = jobs_collection.find_one(sort=[("_id", -1)])
            if max_job:
                max_job_id = max_job["_id"]
        
        if counters_collection.count_documents({"_id": "job_id"}) == 0:
            counters_collection.insert_one({
                "_id": "job_id",
                "sequence_value": max_job_id
            })           
        else:           
            current_counter = counters_collection.find_one({"_id": "job_id"})
            if current_counter and current_counter["sequence_value"] < max_job_id:
                counters_collection.update_one(
                    {"_id": "job_id"},
                    {"$set": {"sequence_value": max_job_id}}
                )
                # print(f"Job ID 카운터 업데이트 완료 (새 값: {max_job_id})")
        
    except Exception as e:
        print(f"카운터 초기화 실패: {e}")

def get_next_job_id():
    try:
        counters_collection = db.get_collection('counters')
        result = counters_collection.find_one_and_update(
            {"_id": "job_id"},
            {"$inc": {"sequence_value": 1}},
            return_document=True
        )
        return result["sequence_value"]
    except Exception as e:
        print(f"Job ID 생성 실패: {e}")
        return None

def initialize_database():
    print("=" * 60)
    print("🚀 데이터베이스 시작")
    print("=" * 60)
    try:
        create_collections()
        create_indexes()
        create_initial_gpus()
        create_initial_counters()

        collections = db.db.list_collection_names()
        print(f"\n생성된 컬렉션: {collections}")
        
        # 각 컬렉션의 문서 수 출력
        for collection_name in collections:
            try:
                collection = db.get_collection(collection_name)
                count = collection.count_documents({})
                # print(f"  - {collection_name}: {count}개 문서")
            except Exception as e:
                print(f"  - {collection_name}: 조회 실패 ({e})")
                
    except Exception as e:
        print(f"\n 데이터베이스 초기화 실패: {e}")
        return False

if __name__ == "__main__":
    initialize_database() 