from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies.database import DB_DEPENDENCY
from app.core.utils.abstract_response import BaseResponse
from app.database.models.projects import Project
from app.database.models.users import User
from app.schemes.project_scheme import ProjectResponseScheme
from app.services.auth_service import AUTHSERVICE_DEPENDENCY, UserModel

from .auth_api import oauth2_bearer

router = APIRouter(prefix="/api/project", tags=["Project"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=BaseResponse[List[ProjectResponseScheme]])
def read_all_projects(
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    token: str = Depends(oauth2_bearer),
) -> BaseResponse[List[ProjectResponseScheme]]:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        users_all_projects = db.query(Project).filter(User.id == userdata.id).all()

        users_all_projects_scheme = [
            ProjectResponseScheme.model_validate(
                {
                    **project.__dict__,
                    "members": [""],
                    "tasks": [""],
                    "comments": [""],
                }
            )
            for project in users_all_projects
        ]

        return BaseResponse(
            code=200,
            message="successfully fetched projects",
            status="success",
            table="projects",
            data=users_all_projects_scheme,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
