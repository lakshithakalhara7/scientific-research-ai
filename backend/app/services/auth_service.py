import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


class AuthService:
    """
    Handles Supabase user authentication.

    This client uses the publishable key only for
    validating end-user Supabase Auth access tokens.
    """

    def __init__(self):

        self.supabase_url = os.getenv(
            "SUPABASE_URL"
        )

        self.publishable_key = os.getenv(
            "SUPABASE_PUBLISHABLE_KEY"
        )

        if not self.supabase_url:
            raise RuntimeError(
                "SUPABASE_URL is not configured."
            )

        if not self.publishable_key:
            raise RuntimeError(
                "SUPABASE_PUBLISHABLE_KEY is not configured."
            )

        self.auth_client = create_client(
            self.supabase_url,
            self.publishable_key
        )

    def verify_access_token(self, token):
        """
        Validate a Supabase Auth user access token.
        """

        if not token:
            return {
                "authenticated": False,
                "user": None,
                "reason": "Access token is missing."
            }

        try:

            response = self.auth_client.auth.get_user(
                token
            )

            user = response.user

            if user is None:
                return {
                    "authenticated": False,
                    "user": None,
                    "reason": (
                        "Invalid authentication token."
                    )
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
                    "Authentication failed or "
                    "the token is invalid."
                )
            }