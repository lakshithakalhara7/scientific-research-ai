from app.core.supabase_client import get_supabase_client


class AuthService:
    """
    Handles authentication and access-token validation
    using Supabase Auth.
    """

    def verify_access_token(self, token):
        """
        Verify a Supabase access token and return
        basic authenticated-user information.
        """

        if not token:
            return {
                "authenticated": False,
                "user": None,
                "reason": "Access token is missing."
            }

        try:
            supabase = get_supabase_client()

            response = supabase.auth.get_user(token)

            user = response.user

            if user is None:
                return {
                    "authenticated": False,
                    "user": None,
                    "reason": "Invalid authentication token."
                }

            return {
                "authenticated": True,
                "user": {
                    "id": str(user.id),
                    "email": user.email
                },
                "reason": None
            }

        except Exception:
            return {
                "authenticated": False,
                "user": None,
                "reason": (
                    "Authentication failed or the token is invalid."
                )
            }