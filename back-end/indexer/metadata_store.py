import json
import os
from datetime import datetime


class MetadataStore:
    def __init__(self, storage_path="metadata_store.json"):
        self.storage_path = storage_path
        self.metadata = {}
        self.load()

    def load(self):
        """저장된 메타데이터 불러오기"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"메타데이터 로드 중 오류 발생: {e}")
                self.metadata = {}

    def save(self):
        """현재 메타데이터 저장"""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"메타데이터 저장 중 오류 발생: {e}")

    def update_file_metadata(self, uuid: str, node_data: dict):
        """파일 메타데이터 업데이트"""
        self.metadata[uuid] = {
            "path": node_data["path"],
            "name": node_data["name"],
            "is_directory": node_data["is_directory"],
            "metadata": node_data["metadata"],
            "description": node_data.get("description", ""),
            "modified_time": node_data["metadata"].get("modified", ""),
            "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.save()
        return True

    def get_file_metadata(self, uuid: str):
        """파일 메타데이터 조회"""
        return self.metadata.get(uuid)

    def remove_metadata(self, uuid: str):
        """파일 메타데이터 제거"""
        if uuid in self.metadata:
            del self.metadata[uuid]
            self.save()  # 삭제 후 저장
