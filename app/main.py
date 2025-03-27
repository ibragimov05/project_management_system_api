import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(title="Project management system API", docs_url=None, redoc_url=None)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "HEALTHY"}


SECURITY = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(SECURITY)) -> str:
    username: str = "admin"
    password: str = "Admin"

    is_username_correct: bool = secrets.compare_digest(credentials.username, username)
    is_password_correct: bool = secrets.compare_digest(credentials.password, password)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(username: str = Depends(verify_credentials)) -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Secure Swagger Ui")


@app.get("/openapi.json", include_in_schema=False)
def get_open_api_scheme(username: str = Depends(verify_credentials)) -> JSONResponse:
    return JSONResponse(app.openapi())
