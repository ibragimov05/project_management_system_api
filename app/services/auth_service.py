import logging

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.database.models.users import User


class UserModel(BaseModel):
    id: int
    username: str
    email: str
    super_admin: bool


class AuthService:
    def __init__(self) -> None:
        self.bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = "69iCD+YYVjQg6KAcCqxn5oNtY+24rIfj04geErTTOqk="
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_DAYS = 1
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.bcrypt_context.verify(plain_password, hashed_password)

    def create_token(self, user: User, refresh_token: bool) -> str:
        to_encode: dict[str, any] = {
            "sub": user.username,
            "id": user.id,
            "email": user.email,
            "super_admin": user.super_admin,
            "refresh_token": refresh_token,
        }

        if refresh_token:
            expire: datetime = datetime.now() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expire: datetime = datetime.now() + timedelta(days=self.ACCESS_TOKEN_EXPIRE_DAYS)

        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        logging.log(msg=f"TOKEN: {token}", level=1)
        return token

    def hash_password(self, plain_password: str) -> str:
        return self.bcrypt_context.hash(plain_password)

    def decode_token(self, token: str) -> dict[str, any]:
        return jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

    def verify_token(self, token: str) -> UserModel | str:
        """
        Helper function to verify and decode the JWT token.\n
        Returns UserModel if token is valid, otherwise `str` the message of error.
        """
        try:
            payload: dict[str, any] = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            username: str = payload.get("sub")
            email: str = payload.get("email")
            superadmin: bool = payload.get("super_admin", False)
            user_id: bool = payload.get("id")

            if not username or not email or not user_id:
                return "Invalid token."

            return UserModel(email=email, id=user_id, super_admin=superadmin, username=username)
        except ExpiredSignatureError:
            return "Token has expired"
        except JWTError:
            return "Invalid or expired token"


def get_auth_service() -> AuthService:
    return AuthService()


AUTH_SERVICE_DEPENDENCY = Annotated[AuthService, Depends(get_auth_service)]
