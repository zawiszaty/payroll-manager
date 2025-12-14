"""Authentication middleware for setting current user context."""

import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.modules.auth.application.services import AuthenticationService
from app.shared.infrastructure.context import set_current_user_id

logger = logging.getLogger(__name__)


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract user from JWT and set in context."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Reset context for each request
        set_current_user_id(None)

        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Try to extract user from Authorization header
        authorization: str | None = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            try:
                # Decode token to get user ID
                payload = AuthenticationService.decode_access_token(token)
                if payload and "sub" in payload:
                    from uuid import UUID

                    user_id = UUID(payload["sub"])
                    set_current_user_id(user_id)
                    logger.info(f"Set current user ID in context: {user_id}")
            except Exception as e:
                # If token is invalid, just continue without user context
                logger.warning(f"Failed to decode token: {e}")

        response = await call_next(request)
        return response
