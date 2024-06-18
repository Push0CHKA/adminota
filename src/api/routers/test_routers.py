from fastapi import APIRouter


router = APIRouter(prefix="/test")


@router.get("/ping", tags=["Test"])
async def ping_pong():
    """Test"""
    return "pong"
