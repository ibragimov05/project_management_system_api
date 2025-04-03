from secrets import compare_digest
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordRequestForm

from app.core.dependencies.database import DB_DEPENDENCY
from app.core.dependencies.rate_limiter import RATE_LIMITER
from app.core.utils.constants import ADMIN_PASSWORD, ADMIN_USERNAME
from app.database.models.users import User
from app.schemes.token_scheme import TokenResponseScheme
from app.services.auth_service import AUTHSERVICE_DEPENDENCY

router = APIRouter(prefix="", tags=["Core"])


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
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Secure Swagger UI")


@router.get("/openapi.json", include_in_schema=False)
def get_open_api_scheme(username: str = Depends(_verify_credentials)) -> JSONResponse:
    from fastapi import Request

    async def get_schema(request: Request):
        app: Any = request.app
        return JSONResponse(app.openapi())

    return get_schema


@router.post("/token", response_model=TokenResponseScheme, dependencies=RATE_LIMITER)
async def get_token(
    db: DB_DEPENDENCY,
    authservice: AUTHSERVICE_DEPENDENCY,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponseScheme:
    try:
        user: User | None = db.query(User).filter(User.username == form_data.username).first()

        # user not found
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        # password is incorrect
        if not authservice.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        # user's account is not active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please contact support.",
            )

        access_token: str = authservice.create_token(user=user, refresh_token=False)
        refresh_token: str = authservice.create_token(user=user, refresh_token=True)

        return TokenResponseScheme(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
