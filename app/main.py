from secrets import compare_digest

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette_admin.contrib.sqla import Admin, ModelView

from app.api.routes.auth_api import router as auth_router
from app.database.base import Base, engine
from app.database.models import User

app = FastAPI(title="Project management system API", docs_url=None, redoc_url=None)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "HEALTHY"}


Base.metadata.create_all(bind=engine)


SECURITY = HTTPBasic()


def _verify_credentials(credentials: HTTPBasicCredentials = Depends(SECURITY)) -> str:
    username: str = "admin"
    password: str = "Admin"

    is_username_correct: bool = compare_digest(credentials.username, username)
    is_password_correct: bool = compare_digest(credentials.password, password)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(username: str = Depends(_verify_credentials)) -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Secure Swagger Ui")


@app.get("/openapi.json", include_in_schema=False)
def get_open_api_scheme(username: str = Depends(_verify_credentials)) -> JSONResponse:
    return JSONResponse(app.openapi())


def _init_routes() -> None:
    all_routes: list[APIRouter] = [auth_router]

    for route in all_routes:
        app.include_router(route)


def _init_starlette() -> None:
    admin = Admin(engine=engine, title="Project management system API")

    admin.mount_to(app)

    all_db_models: list[any] = [User]

    for model in all_db_models:
        admin.add_view(ModelView(model))


_init_routes()
_init_starlette()
