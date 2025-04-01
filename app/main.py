from math import ceil
from typing import NoReturn

import redis.asyncio as redis

from fastapi import APIRouter, FastAPI, HTTPException, Request, Response, status
from fastapi.concurrency import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView

from app.api.routes.auth_api import router as auth_router
from app.api.routes.core_api import router as core_router
from app.api.routes.project_api import router as project_router
from app.core.utils.constants import PROJECT_MANAGEMENT_SYSTEM_API, SESSION_SECRET_KEY
from app.core.utils.starlette_auth_provider import StarletteAuthProvider
from app.database.base import Base, engine
from app.database.models.comments import Comment
from app.database.models.project_members import ProjectMember
from app.database.models.projects import Project
from app.database.models.tasks import Task
from app.database.models.users import User

# @app.middleware("http")
# async def telegram_logger(request: Request, call_next) -> Any | Response:
#     # Log the incoming request
#     request_info = f"Request: {request.method} {request.url}"

#     telegram_bot_service = TelegramBotService()

#     telegram_bot_service.send_telegram_message(request_info)

#     # Process the request and get the response
#     response: Response = await call_next(request)

#     # Log the outgoing response
#     response_info = f"Response: {response.status_code} for {request.url}"
#     telegram_bot_service.send_telegram_message(response_info)

#     return response


async def service_name_identifier(request: Request) -> str | None:
    service: str | None = request.headers.get("Service-Name")

    return service


async def custom_callback(request: Request, response: Response, pexpire: int) -> NoReturn:
    expire: int = ceil(pexpire / 1000)

    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"Too Many Requests. Retry after {expire} seconds.",
        headers={"Retry-After": str(expire)},
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url("redis://localhost:6379/0", encoding="utf8")

    await FastAPILimiter.init(
        redis=redis_connection,
        identifier=service_name_identifier,
        http_callback=custom_callback,
    )

    yield

    await FastAPILimiter.close()


app = FastAPI(title=PROJECT_MANAGEMENT_SYSTEM_API, docs_url=None, redoc_url=None, lifespan=lifespan)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "HEALTHY"}


Base.metadata.create_all(bind=engine)


def _init_routes() -> None:
    all_routes: list[APIRouter] = [core_router, auth_router, project_router]

    for route in all_routes:
        app.include_router(route)


def _init_starlette() -> None:
    admin = Admin(engine=engine, title=PROJECT_MANAGEMENT_SYSTEM_API, auth_provider=StarletteAuthProvider())

    admin.mount_to(app)

    all_db_models: list[any] = [User, Comment, ProjectMember, Project, Task]

    for model in all_db_models:
        admin.add_view(ModelView(model))


app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

_init_routes()
_init_starlette()
