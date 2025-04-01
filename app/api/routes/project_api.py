from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload

from app.core.dependencies.database import DB_DEPENDENCY
from app.core.enums.user_role_enum import UserRole
from app.core.utils.abstract_response import BaseResponse
from app.database.models.projects import Project
from app.database.models.users import User
from app.schemes.project_scheme import CreateProjectScheme, ProjectResponseScheme, UpdateProjectScheme
from app.services.auth_service import AUTHSERVICE_DEPENDENCY, UserModel
from app.services.logger_service import logger

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

        users_all_projects: List[Project] = (
            db.query(Project)
            .options(joinedload(Project.comments), joinedload(Project.members), joinedload(Project.tasks))
            .filter(User.id == userdata.id)
            .all()
        )

        users_all_projects_scheme = [ProjectResponseScheme.model_validate(project) for project in users_all_projects]

        return BaseResponse(
            code=200,
            message="successfully fetched projects",
            status="success",
            table="projects",
            data=users_all_projects_scheme,
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BaseResponse[ProjectResponseScheme])
def create_project(
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    project_scheme: CreateProjectScheme,
    token: str = Depends(oauth2_bearer),
) -> BaseResponse[ProjectResponseScheme]:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        new_project = Project(
            name=project_scheme.name,
            description=project_scheme.description,
            start_date=project_scheme.start_date,
            deadline=project_scheme.deadline,
        )

        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return BaseResponse(
            code=201,
            message="new project has been created successfully",
            status="created",
            table="projects",
            data=new_project,
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_project(
    project_id: int,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    project_scheme: UpdateProjectScheme,
    token: str = Depends(oauth2_bearer),
) -> None:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        if userdata.role == UserRole.TEAM_MEMBER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to create new project. Only ADMIN's or PROJECT MANAGER's are allowed to create",
            )

        project: Project | None = db.query(Project).filter(User.id == userdata.id, Project.id == project_id).first()

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project with the given id not found")

        for key, value in project_scheme.model_dump().items():
            setattr(project, key, value)

        db.add(project)
        db.commit()
        db.refresh(project)

        return None
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    token: str = Depends(oauth2_bearer),
) -> None:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        if userdata.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to delete project. Only ADMIN's are allowed to delete",
            )

        project: Project | None = db.query(Project).filter(User.id == userdata.id, Project.id == project_id).first()

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project with the given id not found")

        db.delete(project)
        db.commit()

        return None
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
