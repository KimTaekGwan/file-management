from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from indexer.filesystem import FileSystem
from indexer.scanner import FileSystemScanner
from monitor.observer import target_folder_path

router = APIRouter()


file_system: Optional[FileSystem] = None


def initialize_router(fs: FileSystem):
    global file_system
    file_system = fs


def get_filesystem() -> FileSystem:
    global file_system
    if not file_system:
        raise HTTPException(status_code=500, detail="FileSystem not initialized")
    print(
        f"Debug - get_filesystem() returning FileSystem instance: {id(file_system)}"
    )  # 인스턴스 ID 출력
    return file_system


@router.get("/filesystem/tree")
async def get_filesystem_tree():
    """전체 파일 시스템 트리 구조 반환"""
    if not file_system:
        raise HTTPException(status_code=404, detail="File system not initialized")
    if not file_system.root:
        print(f"Debug - Root node is missing. Total nodes: {len(file_system.nodes)}")
        print(
            f"Debug - Available nodes: {[node.name for node in file_system.nodes.values()]}"
        )
        raise HTTPException(
            status_code=500, detail="File system root is not initialized"
        )

    def node_to_dict(node):
        result = {
            "uuid": node.uuid,
            "name": node.name,
            "path": node.path,
            "is_directory": node.is_directory,
            "metadata": node.metadata,
            "children": [
                node_to_dict(child)
                for child in sorted(node.children, key=lambda x: x.name)
            ],
        }
        print(
            f"Debug - Processing node: {node.name} with {len(node.children)} children"
        )  # 디버깅 로그
        return result

    tree = node_to_dict(file_system.root)
    print(
        f"Debug - Final tree root has {len(tree['children'])} children"
    )  # 디버깅 로그
    return tree


@router.get("/filesystem/search")
async def search_filesystem(query: str):
    """파일 시스템 검색"""
    if not file_system:
        raise HTTPException(status_code=404, detail="File system not initialized")

    results = []
    for uuid, node in file_system.nodes.items():
        if query.lower() in node.name.lower():
            results.append(
                {
                    "uuid": node.uuid,
                    "name": node.name,
                    "path": node.path,
                    "is_directory": node.is_directory,
                    "metadata": node.metadata,
                }
            )
    return results


@router.get("/filesystem/node/{node_uuid}")
async def get_node_details(node_uuid: str):
    """특정 노드의 상세 정보 조회"""
    if not file_system:
        raise HTTPException(status_code=404, detail="File system not initialized")

    node = file_system.nodes.get(node_uuid)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    return {
        "uuid": node.uuid,
        "name": node.name,
        "path": node.path,
        "is_directory": node.is_directory,
        "metadata": node.metadata,
        "children": [
            {"uuid": child.uuid, "name": child.name} for child in node.children
        ],
    }


@router.post("/filesystem/refresh")
async def refresh_filesystem():
    """파일 시스템 상태 새로고침"""
    if not file_system:
        raise HTTPException(status_code=404, detail="File system not initialized")

    # 파일 시스템 스캐너 재실행
    scanner = FileSystemScanner(target_folder_path, file_system)
    scanner.scan()

    return {"status": "success", "message": "File system refreshed"}


# 여기에 추가 API 엔드포인트를 정의할 수 있습니다
