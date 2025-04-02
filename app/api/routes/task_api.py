from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies.database import DB_DEPENDENCY
from app.core.dependencies.rate_limiter import RATE_LIMITER
from app.core.utils.abstract_response import BaseResponse
from app.database.models.projects import Project
from app.database.models.tasks import Task
from app.schemes.task_scheme import CreateTaskScheme, TaskResponseScheme
from app.services.auth_service import AUTHSERVICE_DEPENDENCY, UserModel
from app.services.logger_service import logger

from .auth_api import oauth2_bearer

router = APIRouter(prefix="/api/task", tags=["Task"])


@router.get(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[List[TaskResponseScheme]],
    dependencies=RATE_LIMITER,
)
def read_all_tasks(
    project_id: int,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    token: str = Depends(oauth2_bearer),
) -> BaseResponse[List[TaskResponseScheme]]:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        project: Project | None = db.query(Project).filter(Project.id == project_id).first()

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project with the given id not found")

        all_tasks: List[Task] = db.query(Task).filter(Project.id == project_id).all()

        all_tasks_scheme: List[TaskResponseScheme] = [TaskResponseScheme.model_validate(task) for task in all_tasks]

        return BaseResponse(
            code=200,
            message="successfully fetched tasks",
            status="success",
            table="tasks",
            data=all_tasks_scheme,
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TaskResponseScheme],
    dependencies=RATE_LIMITER,
)
def create_new_task(
    task_scheme: CreateTaskScheme,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    token: str = Depends(oauth2_bearer),
) -> BaseResponse[TaskResponseScheme]:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        project: Project | None = db.query(Project).filter(Project.id == task_scheme.project_id).first()

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project with the given id not found")

        

    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
