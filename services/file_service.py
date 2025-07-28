import os
from typing import List, Optional

from models import FileItem, DirectoryContent 

class FileService:
    def __init__(self, base_remote_path: str):  # fileSerivice 초기화
        self.base_remote_path = base_remote_path

    async def _get_absolute_path(self, relative_path: str) -> str:  # 상대 경로를 기반 경로와 결합하여 절대 경로를 반환
        # `os.path.abspath`는 실제 경로를 정규화합니다.
        # `base_remote_path`가 '/'와 같은 절대 경로로 시작해야 합니다.
        abs_path = os.path.abspath(os.path.join(self.base_remote_path, relative_path.lstrip('/')))
        
        # `abs_path`가 `base_remote_path`의 하위 경로인지 확인하여 상위 디렉토리 접근을 방지합니다.
        if not abs_path.startswith(os.path.abspath(self.base_remote_path)):
            raise ValueError("잘못된 경로 접근 시도: 기본 경로 외부의 디렉토리에 접근할 수 없습니다.")
        return abs_path

    async def list_directory_contents(self, path: str = "") -> DirectoryContent:    # 디렉토리 내용 list,
        # paths는 base_remote_path에 대한 상대 경로
        full_path = await self._get_absolute_path(path) 

        if not os.path.isdir(full_path):
            raise FileNotFoundError(f"Directory not found: {path}")

        items: List[FileItem] = []
        try:
            with os.scandir(full_path) as entries:
                for entry in entries:
                    is_dir = entry.is_dir()
                    # `os.path.join(path, entry.name)`은 상대 경로를 올바르게 만듭니다.
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
            # 파일을 바이너리 모드로 읽습니다.
            with open(full_path, "rb") as f:
                return f.read() 
        except Exception as e:
            raise IOError(f"Failed to read file: {e}")