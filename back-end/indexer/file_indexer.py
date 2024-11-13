import os
import json
from datetime import datetime
from typing import Optional, List, Dict

class FileIndexer:
    def __init__(self, log_directory: str):
        self.log_directory = log_directory
        self.index: Dict[str, dict] = {}  # path -> metadata
        self.history: List[dict] = []
        self.ensure_log_directory()
        self.load_index()
        self.load_history()

    def ensure_log_directory(self):
        """로그 디렉토리 생성"""
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

    def load_index(self):
        """인덱스 파일 로드"""
        index_path = os.path.join(self.log_directory, "file_index.json")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                self.index = json.load(f)

    def load_history(self):
        """히스토리 파일 로드"""
        history_path = os.path.join(self.log_directory, "file_history.json")
        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                self.history = json.load(f)

    def save_index(self):
        """인덱스 저장"""
        index_path = os.path.join(self.log_directory, "file_index.json")
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def save_history(self):
        """히스토리 저장"""
        history_path = os.path.join(self.log_directory, "file_history.json")
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add_event(self, event_type: str, file_path: str, metadata: dict):
        """파일 시스템 이벤트 기록"""
        timestamp = datetime.now().isoformat()
        event = {
            "timestamp": timestamp,
            "event_type": event_type,
            "file_path": file_path,
            "metadata": metadata
        }
        self.history.append(event)
        self.save_history()

        # 인덱스 업데이트
        if event_type != "deleted":
            self.index[file_path] = {
                "last_modified": timestamp,
                "metadata": metadata
            }
        else:
            self.index.pop(file_path, None)
        self.save_index()

    def get_file_history(self, file_path: Optional[str] = None, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        event_type: Optional[str] = None) -> List[dict]:
        """파일 변경 이력 조회"""
        filtered_history = self.history

        if file_path:
            filtered_history = [
                event for event in filtered_history 
                if event["file_path"] == file_path
            ]

        if start_date:
            start = datetime.fromisoformat(start_date)
            filtered_history = [
                event for event in filtered_history 
                if datetime.fromisoformat(event["timestamp"]) >= start
            ]

        if end_date:
            end = datetime.fromisoformat(end_date)
            filtered_history = [
                event for event in filtered_history 
                if datetime.fromisoformat(event["timestamp"]) <= end
            ]

        if event_type:
            filtered_history = [
                event for event in filtered_history 
                if event["event_type"] == event_type
            ]

        return filtered_history

    def get_file_metadata(self, file_path: str) -> Optional[dict]:
        """파일 메타데이터 조회"""
        return self.index.get(file_path)

    def get_statistics(self) -> dict:
        """파일 시스템 통계 정보"""
        return {
            "total_files": len(self.index),
            "total_events": len(self.history),
            "last_event": self.history[-1]["timestamp"] if self.history else None,
            "event_types": {
                "created": len([e for e in self.history if e["event_type"] == "created"]),
                "modified": len([e for e in self.history if e["event_type"] == "modified"]),
                "deleted": len([e for e in self.history if e["event_type"] == "deleted"])
            }
        }
