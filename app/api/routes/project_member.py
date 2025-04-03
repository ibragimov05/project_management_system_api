from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies.database import DB_DEPENDENCY
from app.core.dependencies.rate_limiter import RATE_LIMITER
from app.core.enums.user_role_enum import UserRole
from app.core.utils.abstract_response import BaseResponse
from app.database.models.projects import Project
from app.database.models.users import User
from app.schemes.member_scheme import ProjectMemberBaseScheme
from app.schemes.project_scheme import ProjectResponseScheme
from app.services.auth_service import AUTHSERVICE_DEPENDENCY, UserModel
from app.services.logger_service import logger

from .auth_api import oauth2_bearer

router = APIRouter(prefix="/api/project_member", tags=["Project member"])


@router.put(
    "/add",
    status_code=status.HTTP_200_OK,
    dependencies=RATE_LIMITER,
    response_model=BaseResponse[ProjectResponseScheme],
)
def add_project_member_to_project(
    member_scheme: ProjectMemberBaseScheme,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    token: str = Depends(oauth2_bearer),
) -> BaseResponse[ProjectResponseScheme]:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        if userdata.role == UserRole.PROJECT_MANAGER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only ADMIN's and PROJECT_MANAGER's are allowed to add a new project member",
            )

        project: Project | None = (
            db.query(Project).filter(Project.id == member_scheme.project_id, User.id == userdata.id).first()
        )

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project with the given id not found")

        user: User | None = db.query(User).filter(User.id == member_scheme.user_id).first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with the given id not found")

        if user in project.members:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="User already has been assigned to that project",
            )

        project.members.append(user)

        db.commit()
        db.commit()
        db.refresh(project)

        return BaseResponse(
            code=200,
            table="projects",
            status="updated",
            message="new user assigned to the project successfully",
            data=ProjectResponseScheme.model_validate(project),
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    "/remove",
    status_code=status.HTTP_200_OK,
    dependencies=RATE_LIMITER,
    response_model=BaseResponse[ProjectResponseScheme],
)
def remove_project_member_from_project(
    member_scheme: ProjectMemberBaseScheme,
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    token: str = Depends(oauth2_bearer),
) -> BaseResponse[ProjectResponseScheme]:
    try:
        userdata: UserModel | str = authservice.verify_token(token)

        if isinstance(userdata, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userdata)

        if userdata.role == UserRole.PROJECT_MANAGER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only ADMIN's and PROJECT_MANAGER's are allowed to add a new project member",
            )

        project: Project | None = (
            db.query(Project).filter(Project.id == member_scheme.project_id, User.id == userdata.id).first()
        )

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project with the given id not found")

        user: User | None = db.query(User).filter(User.id == member_scheme.user_id).first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with the given id not found")

        if user not in project.members:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="User not in that project",
            )

        project.members.remove(user)

        db.commit()
        db.commit()
        db.refresh(project)

        return BaseResponse(
            code=200,
            table="projects",
            status="remove",
            message="user removed from project successfully",
            data=ProjectResponseScheme.model_validate(project),
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(str(e))

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
