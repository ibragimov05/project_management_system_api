from fastapi import APIRouter

router = APIRouter(prefix="/api/project", tags=["Project"])


@router.get("/")
def read_all_projects():
    return {}
