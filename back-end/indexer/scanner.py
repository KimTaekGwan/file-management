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

        # 루트 노드 생성 및 메타데이터 설정
        root_node = self.file_system.create_node(self.root_path, is_directory=True)
        root_metadata = self.get_metadata(self.root_path)
        root_node.metadata = root_metadata
        
        # FileIndexer에 루트 노드 기록
        self.file_system.file_indexer.add_event(
            event_type="created",
            file_path=self.root_path,
            metadata=root_metadata
        )

        # 파일 시스템 스캔
        for root, dirs, files in os.walk(self.root_path):
            # 디렉토리 처리
            for dir_name in dirs:
                path = os.path.join(root, dir_name)
                try:
                    node = self.file_system.create_node(path, is_directory=True)
                    metadata = self.get_metadata(path)
                    node.metadata = metadata
                    # FileIndexer에 디렉토리 노드 기록
                    self.file_system.file_indexer.add_event(
                        event_type="created",
                        file_path=path,
                        metadata=metadata
                    )
                except Exception as e:
                    logger.error(f"Error creating directory node {path}: {e}")

            # 파일 처리
            for file_name in files:
                path = os.path.join(root, file_name)
                try:
                    node = self.file_system.create_node(path, is_directory=False)
                    metadata = self.get_metadata(path)
                    node.metadata = metadata
                    # FileIndexer에 파일 노드 기록
                    self.file_system.file_indexer.add_event(
                        event_type="created",
                        file_path=path,
                        metadata=metadata
                    )
                except Exception as e:
                    logger.error(f"Error creating file node {path}: {e}")
