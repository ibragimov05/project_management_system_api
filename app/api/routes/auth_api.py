from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.core.dependencies.database import DB_DEPENDENCY
from app.core.utils.abstract_response import BaseResponse
from app.core.utils.helpers import Helpers
from app.database.models.users import User
from app.schemes.token_scheme import TokenResponseScheme
from app.schemes.user_scheme import CreateUserScheme, UserResponseSchema
from app.services.auth_service import AUTH_SERVICE_DEPENDENCY

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/login", status_code=status.HTTP_200_OK, response_model=BaseResponse[dict])
async def login(
    db: DB_DEPENDENCY,
    authservice: AUTH_SERVICE_DEPENDENCY,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> BaseResponse[dict]:
    user: User | None = (
        db.query(User).options(joinedload(User.shops)).filter(User.username == form_data.username).first()
    )

    # user not found
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # password is incorrect
    if not authservice.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # user's account is not active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support.",
        )

    access_token: str = authservice.create_token(user=user, refresh_token=False)
    refresh_token: str = authservice.create_token(user=user, refresh_token=True)

    return BaseResponse(
        code=200,
        table="users",
        message="User logged in successfully",
        status="success",
        data={
            "user": UserResponseSchema.model_validate(user),
            "token": TokenResponseScheme(access_token=access_token, refresh_token=refresh_token),
        },
    )


@router.post("/token", response_model=TokenResponseScheme)
async def get_token(
    db: DB_DEPENDENCY,
    authservice: AUTH_SERVICE_DEPENDENCY,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponseScheme:
    user: User | None = (
        db.query(User).options(joinedload(User.shops)).filter(User.username == form_data.username).first()
    )

    # user not found
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # password is incorrect
    if not authservice.verify_password(form_data.password, user.password_hash):
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


@router.post("/sign_in", status_code=status.HTTP_201_CREATED, response_model=BaseResponse[UserResponseSchema])
async def sign_in(
    db: DB_DEPENDENCY,
    create_user_request: CreateUserScheme,
    authservice: AUTH_SERVICE_DEPENDENCY,
) -> BaseResponse[UserResponseSchema]:
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == create_user_request.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        # Check if username already exists
        existing_user = db.query(User).filter(User.username == create_user_request.username).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

        # Validate email format
        if not Helpers.is_valid_email(create_user_request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email address, please check the format",
            )

        # Create user model
        create_user_model = User(
            username=create_user_request.username,
            email=create_user_request.email,
            telegram_chat_id=create_user_request.telegram_chat_id,
            password_hash=authservice.hash_password(create_user_request.password),
        )

        db.add(create_user_model)
        db.commit()
        db.refresh(create_user_model)

        return BaseResponse(
            code=200,
            message="User created successfully",
            table="users",
            status="success",
            data=create_user_model,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate email or username")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/refresh", status_code=status.HTTP_200_OK, response_model=BaseResponse[TokenResponseScheme])
async def refresh_token(
    db: DB_DEPENDENCY,
    refresh_token: str,
    authservice: AUTH_SERVICE_DEPENDENCY,
) -> BaseResponse[TokenResponseScheme]:
    try:
        payload: dict[str, any] = authservice.decode_token(refresh_token)

        is_refresh_token: bool | None = payload.get("refresh_token")
        username: str | None = payload.get("sub")

        if not is_refresh_token or is_refresh_token is None or username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user: User | None = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        new_access_token: str = authservice.create_token(user=user, refresh_token=False)
        new_refresh_token: str = authservice.create_token(user=user, refresh_token=True)

        return BaseResponse(
            code=200,
            message="token refreshed successfully",
            status="success",
            table="none",
            data=TokenResponseScheme(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
            ),
        )

    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")
    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
