"""Load backend-only Supabase settings when explicitly requested."""

from functools import lru_cache
from pathlib import Path

from pydantic import (
    Field,
    HttpUrl,
    SecretStr,
    ValidationError,
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


BACKEND_ENV_FILE = (
    Path(__file__).resolve().parents[2] / ".env"
)


class SupabaseConfigurationError(ValueError):
    """
    Missing or invalid Supabase configuration.
    Credential values are never exposed.
    """


class SupabaseSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=BACKEND_ENV_FILE,
        env_file_encoding="utf-8-sig",
        extra="ignore",
        hide_input_in_errors=True,
        frozen=True,
    )

    supabase_url: HttpUrl = Field(
        repr=False
    )

    supabase_secret_key: SecretStr = Field(
        repr=False
    )

    @field_validator("supabase_url")
    @classmethod
    def validate_project_url(
        cls,
        value: HttpUrl
    ) -> HttpUrl:

        if (
            value.username
            or value.password
            or value.query
            or value.fragment
        ):
            raise ValueError(
                "Use the project URL without credentials "
                "or query parameters."
            )

        if value.path not in (None, "/"):
            raise ValueError(
                "Use the project root URL, "
                "without an API path."
            )

        return value

    @field_validator("supabase_secret_key")
    @classmethod
    def validate_secret_key(
        cls,
        value: SecretStr
    ) -> SecretStr:

        secret = (
            value
            .get_secret_value()
            .strip()
        )

        if not secret:
            raise ValueError(
                "A non-empty backend secret key is required."
            )

        if secret.startswith(
            "sb_publishable_"
        ):
            raise ValueError(
                "Use a backend secret key, "
                "not a publishable key."
            )

        return SecretStr(secret)


@lru_cache(maxsize=1)
def get_settings() -> SupabaseSettings:
    """
    Load Supabase backend configuration.

    Environment variables override backend/.env.
    """

    try:
        return SupabaseSettings()

    except ValidationError as error:

        fields = sorted({
            str(issue["loc"][0]).upper()
            for issue in error.errors(
                include_input=False,
                include_context=False
            )
        })

        raise SupabaseConfigurationError(
            "Missing or invalid Supabase configuration: "
            + ", ".join(fields)
            + ". Set these environment variables or "
            "configure backend/.env. "
            "See backend/.env.example."
        ) from None

    except (OSError, UnicodeError):

        raise SupabaseConfigurationError(
            "Cannot read backend/.env; "
            "check file permissions and UTF-8 encoding."
        ) from None