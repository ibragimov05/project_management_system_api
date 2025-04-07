from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies.database import DB_DEPENDENCY
from app.core.dependencies.rate_limiter import RATE_LIMITER
from app.core.utils.abstract_response import BaseResponse
from app.database.models.comments import Comment
from app.database.models.projects import Project
from app.database.models.users import User
from app.schemes.comment_scheme import CommentResponseScheme
from app.services.auth_service import AUTHSERVICE_DEPENDENCY, UserModel
from app.services.logger_service import logger

from .auth_api import oauth2_bearer

router = APIRouter(prefix="/api/comment", tags=["Comment"])


@router.get(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[List[CommentResponseScheme]],
    dependencies=RATE_LIMITER,
)
def read_projects_all_comments(
    project_id: int,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    token: str = Depends(oauth2_bearer),
) -> BaseResponse[List[CommentResponseScheme]]:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        project: Project | None = db.query(Project).filter(Project.id == project_id, User.id == userdata.id).first()

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project with the given id not found")

        all_comments: List[Comment] = db.query(Comment).filter(Project.id == project.id).all()

        all_comments_scheme: List[CommentResponseScheme] = [
            CommentResponseScheme.model_validate(comment) for comment in all_comments
        ]

        return BaseResponse(
            code=200,
            message="successfully fetched comments",
            status="success",
            table="comments",
            data=all_comments_scheme,
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
