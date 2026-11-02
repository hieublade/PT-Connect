from fastapi import APIRouter

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "UP",
        "message": "PT-Connect Backend is healthy",
    }
