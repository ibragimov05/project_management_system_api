from app.core.utils.constants import ADMIN_PASSWORD, ADMIN_USERNAME


from typing import Any

from fastapi import Response
from starlette_admin.auth import AuthProvider
from starlette_admin.exceptions import LoginFailed



class StarletteAuthProvider(AuthProvider):
    async def login(self, username, password, remember_me, request, response) -> Response:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session.update({"username": username, "authenticated": True})
            return response

        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        return request.session.get("authenticated", False)

    def get_admin_user(self, request) -> dict[str, Any | None]:
        return {"username": request.session.get("username")}

    async def logout(self, request, response) -> Response:
        request.session.clear()

        return response
