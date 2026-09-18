from fastapi import Header, HTTPException

from app.services.auth_service import AuthService


auth_service = AuthService()


def get_current_user(
    authorization: str | None = Header(default=None)
):
    """
    Require a valid Bearer token before allowing
    access to a protected API endpoint.
    """

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication is required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header."
        )

    token = authorization.removeprefix(
        "Bearer "
    ).strip()

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