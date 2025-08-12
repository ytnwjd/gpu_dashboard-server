import os
from typing import List, Optional

from models import FileItem, DirectoryContent 

class FileService:
    def __init__(self, base_remote_path: str):
        self.base_remote_path = base_remote_path

    async def _get_absolute_path(self, relative_path: str) -> str:  # 상대 경로를 기반 경로와 결합하여 절대 경로를 반환
        abs_path = os.path.abspath(os.path.join(self.base_remote_path, relative_path.lstrip('/')))
        
        if not abs_path.startswith(os.path.abspath(self.base_remote_path)):
            raise ValueError("잘못된 경로 접근 시도: 기본 경로 외부의 디렉토리에 접근할 수 없습니다.")
        return abs_path

    async def list_directory_contents(self, path: str = "") -> DirectoryContent:    # 디렉토리 내용 list
        full_path = await self._get_absolute_path(path) 

        if not os.path.isdir(full_path):
            raise FileNotFoundError(f"Directory not found: {path}")

        items: List[FileItem] = []
        try:
            with os.scandir(full_path) as entries:
                for entry in entries:
                    is_dir = entry.is_dir()                    
                    item_path = os.path.join(path, entry.name).replace('\\', '/') # Windows 호환성
                    item_size = entry.stat().st_size if entry.is_file() else None
                    item_modified = entry.stat().st_mtime
                    items.append(FileItem(
                        name=entry.name,
                        is_directory=is_dir,
                        path=item_path,
                        size=item_size,
                        last_modified=item_modified
                    ))
        except Exception as e:
            raise IOError(f"Failed to list directory contents: {e}")

        items.sort(key=lambda x: (not x.is_directory, x.name.lower()))  # 디렉토리와 파일을 구분하여 정렬

        return DirectoryContent(current_path=path, items=items)

    async def download_file(self, path: str) -> bytes:  # 실제 파일을 바이트로 읽어 반환
        full_path = await self._get_absolute_path(path)

        if not os.path.isfile(full_path):
            raise FileNotFoundError(f"File not found: {path}")
        
        try:            
            with open(full_path, "rb") as f:
                return f.read() 
        except Exception as e:
            raise IOError(f"Failed to read file: {e}")