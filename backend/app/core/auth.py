from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from app.services.auth_service import AuthService


auth_service = AuthService()

bearer_scheme = HTTPBearer(
    auto_error=False
)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme)
    ]
):
    """
    Require a valid Supabase Bearer access token
    before allowing access to protected endpoints.
    """

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication is required."
        )

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication token is missing."
        )

    result = auth_service.verify_access_token(
        token
    )

    if not result["authenticated"]:
        raise HTTPException(
            status_code=401,
            detail=result["reason"]
        )

    return result["user"]