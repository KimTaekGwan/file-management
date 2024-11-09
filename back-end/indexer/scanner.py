import os
from datetime import datetime
from indexer.filesystem import FileSystem
import logging

logger = logging.getLogger(__name__)


class FileSystemScanner:
    def __init__(self, root_path: str, file_system: FileSystem):
        self.root_path = root_path
        self.file_system = file_system
        self.file_system.root_path = root_path  # root_path 설정

    def get_metadata(self, path: str) -> dict:
        """파일의 메타데이터를 가져옵니다"""
        stat = os.stat(path)
        return {
            "size": stat.st_size,  # 파일 크기 (바이트)
            "created": datetime.fromtimestamp(stat.st_ctime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),  # 생성일시
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),  # 수정일시
            "is_hidden": os.path.basename(path).startswith("."),  # 숨김 파일 여부
            "permissions": oct(stat.st_mode)[-3:],  # 파일 권한
            "owner": stat.st_uid,  # 소유자 ID
            "group": stat.st_gid,  # 그룹 ID
        }

    def scan(self) -> None:
        """초기 파일 시스템 스캔"""
        print(f"Starting scan of {self.root_path}")
        # 먼저 루트 디렉토리 생성
        if not os.path.exists(self.root_path):
            print(f"Creating directory: {self.root_path}")
            os.makedirs(self.root_path)

        root_node = self.file_system.create_node(self.root_path, is_directory=True)
        print(f"Root node created: {root_node.uuid}")
        print(
            f"FileSystem root node: {self.file_system.root.uuid if self.file_system.root else None}"
        )
        root_node.metadata = self.get_metadata(self.root_path)

        # 파일 시스템 스캔
        for root, dirs, files in os.walk(self.root_path):
            # 디렉토리 처리
            for dir_name in dirs:
                path = os.path.join(root, dir_name)
                try:
                    node = self.file_system.create_node(path, is_directory=True)
                    node.metadata = self.get_metadata(path)
                except Exception as e:
                    logger.error(f"Error creating directory node {path}: {e}")

            # 파일 처리
            for file_name in files:
                path = os.path.join(root, file_name)
                try:
                    node = self.file_system.create_node(path, is_directory=False)
                    node.metadata = self.get_metadata(path)
                except Exception as e:
                    logger.error(f"Error creating file node {path}: {e}")
