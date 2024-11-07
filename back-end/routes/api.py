from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

# 여기에 추가 API 엔드포인트를 정의할 수 있습니다