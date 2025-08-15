import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        try:
            mongo_uri = os.getenv('MONGO_URI')
            
            if not mongo_uri:
                host = os.getenv('MONGO_HOST')
                port = os.getenv('MONGO_PORT')
                username = os.getenv('MONGO_USERNAME')
                password = os.getenv('MONGO_PASSWORD')
                database = os.getenv('MONGO_DATABASE')
                auth_source = os.getenv('MONGO_AUTH_SOURCE')
                
                mongo_uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_source}"
            
            self.client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000, 
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            self.client.admin.command('ping')
            print("✅ MongoDB 연결 성공")
            
            database_name = os.getenv('MONGO_DATABASE', 'gpu_dashboard')
            self.db = self.client[database_name]
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB 연결 실패: {e}")
            raise
        except ServerSelectionTimeoutError as e:
            print(f"❌ MongoDB 서버 선택 타임아웃: {e}")
            raise
        except Exception as e:
            print(f"❌ MongoDB 연결 중 오류 발생: {e}")
            raise
    
    def get_collection(self, collection_name):
        if self.db is None:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        return self.db[collection_name]
    
    def close(self):
        if self.client is not None:
            self.client.close()
            print("✅ MongoDB 연결 종료")

db = Database() 