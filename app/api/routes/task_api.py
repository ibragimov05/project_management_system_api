from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.core.dependencies.database import DB_DEPENDENCY
from app.core.dependencies.rate_limiter import RATE_LIMITER
from app.core.enums.user_role_enum import UserRole
from app.core.utils.abstract_response import BaseResponse
from app.core.utils.helpers import Helpers
from app.database.models.projects import Project
from app.database.models.tasks import Task
from app.database.models.users import User
from app.schemes.task_scheme import CreateTaskScheme, TaskResponseScheme, UpdateTaskScheme
from app.services.auth_service import AUTHSERVICE_DEPENDENCY, UserModel
from app.services.email_service import EMAIL_SERVICE_DEPENDENCY
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
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponse[TaskResponseScheme],
    dependencies=RATE_LIMITER,
)
def create_new_task(
    task_scheme: CreateTaskScheme,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    email_service: EMAIL_SERVICE_DEPENDENCY,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_bearer),
) -> BaseResponse[TaskResponseScheme]:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        if userdata.role == UserRole.TEAM_MEMBER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin's or project manager's are allowed to create a new task",
            )

        project: Project | None = db.query(Project).filter(Project.id == task_scheme.project_id).first()

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project with the given id not found")

        assignee_user: User | None = db.query(User).filter(User.id == task_scheme.assignee_id).first()

        if assignee_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="assignee user with the given id not found",
            )

        new_task = Task(
            project_id=task_scheme.project_id,
            title=task_scheme.title,
            description=task_scheme.description,
            assignee_id=task_scheme.assignee_id,
            status=task_scheme.status,
            priority=task_scheme.priority,
            due_to=task_scheme.due_to,
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        # sending email notification to user
        background_tasks.add_task(
            email_service.send_new_task_email,
            assignee_user.email,
            f"New task assigned: {new_task.title}",
            Helpers.get_new_task_assigned_detail(
                task=new_task,
                project_name=project.name,
                username=assignee_user.full_name,
                assigned_by=userdata.full_name,
            ),
        )

        return BaseResponse(
            code=201,
            message="New task created successfully",
            status="success",
            table="tasks",
            data=TaskResponseScheme.model_validate(new_task),
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=RATE_LIMITER)
def update_task(
    task_id: int,
    task_scheme: UpdateTaskScheme,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    email_service: EMAIL_SERVICE_DEPENDENCY,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_bearer),
) -> None:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        project: Project | None = db.query(Project).filter(Project.id == task_scheme.project_id).first()

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project with the given id not found")

        task: Task | None = db.query(Task).filter(Task.id == task_id, Project.id == project.id).first()

        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task with the given id not found")

        for key, value in task_scheme.model_dump().items():
            setattr(project, key, value)

        db.add(task)
        db.commit()
        db.refresh(task)

        assignee_user: User | None = db.query(User).filter(User.id == task_scheme.assignee_id).first()

        # sending email about task being updated
        if assignee_user is not None:
            background_tasks.add_task(
                email_service.send_new_task_email,
                assignee_user.email,
                f"Task updated: {task.title}",
                Helpers.get_task_updated_details(
                    task=task,
                    project_name=project.name,
                    username=assignee_user.full_name,
                    updated_by=userdata.full_name,
                ),
            )

        return None
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=RATE_LIMITER)
def delete_task(
    task_id: int,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    token: str = Depends(oauth2_bearer),
) -> None:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        if userdata.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin's are allowed to delete task")

        task: Task | None = db.query(Task).filter(Task.id == task_id).first()

        db.delete(task)
        db.commit()

        return None
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
