from secrets import compare_digest

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.utils.constants import ADMIN_PASSWORD, ADMIN_USERNAME

router = APIRouter(prefix="", tags=["Core"])


# router = APIRouter(prefix="/api/auth", tags=["Authentication"])

SECURITY = HTTPBasic()


def _verify_credentials(credentials: HTTPBasicCredentials = Depends(SECURITY)) -> str:
    is_username_correct: bool = compare_digest(credentials.username, ADMIN_USERNAME)
    is_password_correct: bool = compare_digest(credentials.password, ADMIN_PASSWORD)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@router.get("/docs", include_in_schema=False)
def custom_swagger_ui(username: str = Depends(_verify_credentials)) -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Secure Swagger Ui")


@router.get("/openapi.json", include_in_schema=False)
def get_open_api_scheme(username: str = Depends(_verify_credentials)) -> JSONResponse:
    # The actual FastAPI app will be accessible through the request
    # We'll fix this in the route registration
    from fastapi import Request

    async def get_schema(request: Request):
        app = request.app  # Get the FastAPI app from the request
        return JSONResponse(app.openapi())

    return get_schema
