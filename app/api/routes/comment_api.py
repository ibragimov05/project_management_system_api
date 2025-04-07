from fastapi import APIRouter

router = APIRouter(prefix="/api/comment", tags=["Comment"])


@router.get("/{project_id}")
def read_projects_all_comments() -> dict:
    pass
