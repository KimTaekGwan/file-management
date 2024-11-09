import os
import uuid
from datetime import datetime
from typing import Optional


class FileNode:
    def __init__(self, name: str, path: str, is_directory: bool = False):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.path = path
        self.is_directory = is_directory
        self.parent = None
        self.children = []
        self.metadata = {}
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modified_at = self.created_at


class FileSystem:
    def __init__(self):
        self.root = None
        self.root_path = None  # root_path 추가
        self.nodes = {}  # uuid -> node
        self.path_index = {}  # path -> uuid
        self.event_handlers = []  # 이벤트 핸들러 리스트

    def subscribe(self, handler):
        """이벤트 핸들러 등록"""
        self.event_handlers.append(handler)

    def notify_event(self, event_type: str, node: FileNode):
        """이벤트 발생 시 등록된 핸들러들에게 통지"""
        for handler in self.event_handlers:
            handler(event_type, node)

    def get_node_by_path(self, path: str) -> Optional[FileNode]:
        """경로로 노드 찾기"""
        return self.nodes.get(self.path_index.get(path))

    def create_node(self, path: str, is_directory: bool = False):
        # 절대 경로로 변환
        abs_path = os.path.abspath(path)

        # 이미 존재하는 노드인지 확인
        if abs_path in self.path_index:
            existing_node = self.nodes[self.path_index[abs_path]]
            print(f"Node already exists: {existing_node.uuid} ({abs_path})")
            return existing_node

        name = os.path.basename(abs_path)
        node = FileNode(name, abs_path, is_directory)

        # 상대 경로로 변환
        rel_path = os.path.relpath(abs_path, start=self.root_path)

        # 루트 디렉토리인 경우
        if rel_path == "." or abs_path == self.root_path:
            if not self.root:
                self.root = node
                print(f"Setting root node: {node.uuid}")
        else:
            # 부모 경로 찾기
            parent_path = os.path.dirname(abs_path)
            parent_node = self.get_node_by_path(parent_path)

            if not parent_node:
                print(f"Creating parent node for: {parent_path}")
                parent_node = self.create_node(parent_path, is_directory=True)

            # 부모-자식 관계 설정
            node.parent = parent_node
            if node not in parent_node.children:  # 중복 방지
                parent_node.children.append(node)
                print(f"Added node {node.uuid} to parent {parent_node.uuid}")

        # 노드 등록
        self.nodes[node.uuid] = node
        self.path_index[abs_path] = node.uuid
        self.notify_event("created", node)

        return node

    def remove_node(self, path: str):
        """노드 제거"""
        if path not in self.path_index:
            print(f"Warning: Node not found for path {path}")
            return

        node_uuid = self.path_index[path]
        node = self.nodes[node_uuid]

        # 자식 노드들도 함께 제거
        children = node.children.copy()  # 복사본 생성
        for child in children:
            self.remove_node(child.path)

        # 부모 노드에서 제거
        if node.parent:
            node.parent.children.remove(node)

        # 루트 노드인 경우
        if self.root and node.uuid == self.root.uuid:
            self.root = None

        # 인덱스에서 제거
        del self.nodes[node_uuid]
        del self.path_index[path]

        print(f"Removed node: {node.uuid} ({path})")
        self.notify_event("deleted", node)

    def update_node(self, path: str, metadata: dict):
        """노드 업데이트"""
        if path not in self.path_index:
            return

        node_uuid = self.path_index[path]
        node = self.nodes[node_uuid]

        # 메타데이터 업데이트
        node.metadata.update(metadata)
        node.modified_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 노드 맵 갱신
        self.nodes[node_uuid] = node
        self.path_index[path] = node_uuid

        # 이벤트 통지
        print(f"Node updated: {node.uuid} ({path})")
        self.notify_event("modified", node)

        return node
