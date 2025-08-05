import os
from typing import List, Optional
import paramiko # SSHv2 프로토콜을 구현
import stat # 파일 시스템의 메타데이터를 확인하고 해석

from models import FileItem, DirectoryContent

class FileService:
    def __init__(self, hostname: str, username: str, port: int, password: Optional[str] = None, key_filename: Optional[str] = None, base_remote_path: str = '/'):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.password = password
        self.key_filename = key_filename
        self.base_remote_path = base_remote_path

    # 원격 서버에 SSH 연결을 설정하고 SFTP 클라이언트를 생성
    def _get_sftp_client(self):        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 원격 서버 연결
        ssh_client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            password=self.password,
            key_filename=self.key_filename
        )
        
        # 연결된 SSH 세션을 통해 SFTP 클라이언트를 열어 파일 시스템 작업 준비
        sftp_client = ssh_client.open_sftp()
        return ssh_client, sftp_client  
    
    # 경로 보안 처리 
    def _get_absolute_path(self, relative_path: str) -> str:
        base_path = self.base_remote_path.rstrip('/')
        clean_relative_path = relative_path.lstrip('/')
    
        path_components = []
        for component in (base_path + '/' + clean_relative_path).split('/'):
            if component == '..':
                if len(path_components) > 0:
                    path_components.pop()
            elif component and component != '.':
                path_components.append(component)

        abs_path = '/' + '/'.join(path_components)

        if not abs_path.startswith(base_path):
            raise ValueError("잘못된 경로 접근 시도: 기본 경로 외부의 디렉토리에 접근할 수 없습니다.")
        
        return abs_path

    async def list_directory_contents(self, path: str = "") -> DirectoryContent:
        full_path = self._get_absolute_path(path)
        ssh_client, sftp_client = self._get_sftp_client()

        try:
            items: List[FileItem] = []
            
            for entry_name in sftp_client.listdir(full_path):   # 경로에 있는 파일 및 폴더 이름 get
                file_stat = sftp_client.stat(f"{full_path}/{entry_name}")
                is_dir = stat.S_ISDIR(file_stat.st_mode)    # 항목이 디렉토리인지 확인
                
                item_path = f"{path.lstrip('/')}/{entry_name}".lstrip('/')
                
                item_size = file_stat.st_size if not is_dir else None
                item_modified = file_stat.st_mtime
                
                items.append(FileItem(  # FileItem 객체 생성 후 list에 추가
                    name=entry_name,
                    is_directory=is_dir,
                    path=item_path,
                    size=item_size,
                    last_modified=item_modified
                ))

            items.sort(key=lambda x: (not x.is_directory, x.name.lower()))
            return DirectoryContent(current_path=path, items=items)

        except IOError as e:
            raise FileNotFoundError(f"Directory not found: {path} - {e}")
        finally:    # 클라이언트 해제
            sftp_client.close()
            ssh_client.close()

    # async def download_file(self, path: str) -> bytes:
    #     full_path = self._get_absolute_path(path)
    #     ssh_client, sftp_client = self._get_sftp_client()
        
    #     try:
    #         with sftp_client.open(full_path, "rb") as remote_file:
    #             return remote_file.read()
    #     except IOError as e:
    #         raise FileNotFoundError(f"File not found or permission denied: {path} - {e}")
    #     finally:
    #         sftp_client.close()
    #         ssh_client.close()