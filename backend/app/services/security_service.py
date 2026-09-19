import os
import re

from dotenv import load_dotenv


load_dotenv()


class SecurityService:
    """
    Provides security checks for user text input
    before it is sent to retrieval or LLM agents.
    """

    MAX_QUERY_LENGTH = 2000

    SUSPICIOUS_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?instructions",
        r"disregard\s+(all\s+)?previous\s+instructions",
        r"reveal\s+(the\s+)?system\s+prompt",
        r"show\s+(the\s+)?system\s+prompt",
        r"print\s+(the\s+)?system\s+prompt",
        r"developer\s+message",
        r"reveal\s+(your\s+)?api\s+key",
        r"show\s+(your\s+)?api\s+key",
        r"bypass\s+(the\s+)?security",
        r"disable\s+(the\s+)?security",
    ]
    SENSITIVE_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

        "phone": r"(?<!\w)\+?\d(?:[\d\s\-]{7,}\d)(?!\w)",

        "api_key": (
            r"\b(?:api[_\- ]?key|secret[_\- ]?key|access[_\- ]?token)"
            r"\s*[:=]\s*[A-Za-z0-9_\-]{8,}\b"
        ),

        "password": (
            r"\bpassword\s*[:=]\s*\S+"
        ),

        "bearer_token": (
            r"\bBearer\s+[A-Za-z0-9._\-]+\b"
        )
    }
    def sanitize_text(self, text):
        """
        Clean basic control characters and unnecessary
        whitespace from user-provided text.
        """

        if not isinstance(text, str):
            return ""

        text = text.replace("\x00", "")

        text = re.sub(
            r"[\r\n\t]+",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def detect_prompt_injection(self, text):
        """
        Detect common prompt-injection patterns.

        This is a heuristic safety check and does not
        guarantee detection of every malicious prompt.
        """

        cleaned_text = self.sanitize_text(text).lower()

        detected_patterns = []

        for pattern in self.SUSPICIOUS_PATTERNS:

            if re.search(
                pattern,
                cleaned_text,
                re.IGNORECASE
            ):
                detected_patterns.append(pattern)

        return {
            "detected": len(detected_patterns) > 0,
            "matches": detected_patterns
        }

    def validate_query(self, query):
        """
        Validate a user research question before
        sending it to the AI pipeline.
        """

        if not isinstance(query, str):
            return {
                "valid": False,
                "reason": "Query must be text."
            }

        cleaned_query = self.sanitize_text(query)

        if not cleaned_query:
            return {
                "valid": False,
                "reason": "Query cannot be empty."
            }

        if len(cleaned_query) > self.MAX_QUERY_LENGTH:
            return {
                "valid": False,
                "reason": (
                    f"Query exceeds the maximum length of "
                    f"{self.MAX_QUERY_LENGTH} characters."
                )
            }

        injection_result = (
            self.detect_prompt_injection(
                cleaned_query
            )
        )

        if injection_result["detected"]:
            return {
                "valid": False,
                "reason": (
                    "The query contains potentially unsafe "
                    "prompt-injection instructions."
                )
            }

        return {
            "valid": True,
            "reason": None,
            "cleaned_query": cleaned_query
        }
    def detect_sensitive_data(self, text):
        """
        Detect potentially sensitive information
        in user-provided text.
        """

        cleaned_text = self.sanitize_text(text)

        detected = {}

        for data_type, pattern in self.SENSITIVE_PATTERNS.items():

            matches = re.findall(
                pattern,
                cleaned_text,
                re.IGNORECASE
            )

            if matches:
                detected[data_type] = matches

        return {
            "detected": len(detected) > 0,
            "types": list(detected.keys()),
            "matches": detected
        }
    def redact_sensitive_data(self, text):
        """
        Redact sensitive information before text
        is sent to external AI services.
        """

        redacted_text = self.sanitize_text(text)

        replacements = {
            "email": "[REDACTED_EMAIL]",
            "phone": "[REDACTED_PHONE]",
            "api_key": "[REDACTED_API_KEY]",
            "password": "[REDACTED_PASSWORD]",
            "bearer_token": "[REDACTED_TOKEN]"
        }

        for data_type, pattern in self.SENSITIVE_PATTERNS.items():

            redacted_text = re.sub(
                pattern,
                replacements[data_type],
                redacted_text,
                flags=re.IGNORECASE
            )

        return redacted_text

    def prepare_safe_query(self, query):
        """
        Validate and prepare a user query before
        sending it to the AI pipeline.

        Personal information such as email addresses
        and phone numbers is redacted.

        Authentication secrets are rejected entirely.
        """

        validation = self.validate_query(query)

        if not validation["valid"]:
            return {
                "safe": False,
                "reason": validation["reason"],
                "query": None,
                "privacy_warning": False,
                "sensitive_types": []
            }

        cleaned_query = validation["cleaned_query"]

        sensitive_result = self.detect_sensitive_data(
            cleaned_query
        )

        sensitive_types = sensitive_result["types"]

        secret_types = {
            "api_key",
            "password",
            "bearer_token"
        }

        detected_secrets = [
            data_type
            for data_type in sensitive_types
            if data_type in secret_types
        ]

        if detected_secrets:
            return {
                "safe": False,
                "reason": (
                    "The query appears to contain authentication "
                    "credentials or secret information. Remove "
                    "the secret before submitting the request."
                ),
                "query": None,
                "privacy_warning": True,
                "sensitive_types": detected_secrets
            }

        safe_query = self.redact_sensitive_data(
            cleaned_query
        )

        return {
            "safe": True,
            "reason": None,
            "query": safe_query,
            "privacy_warning": sensitive_result["detected"],
            "sensitive_types": sensitive_types
        }
    def check_required_environment_variables(self):
        """
        Check whether required environment variables exist
        without revealing their actual secret values.
        """

        required_variables = [
            "GEMINI_API_KEY"
        ]

        missing_variables = []

        for variable in required_variables:

            if not os.getenv(variable):
                missing_variables.append(variable)

        return {
            "configured": len(missing_variables) == 0,
            "missing_variables": missing_variables
        }

    def create_safe_error_response(self, error):
        """
        Convert internal exceptions into safe messages
        without exposing implementation details.
        """

        error_name = type(error).__name__

        if error_name == "ClientError":
            message = (
                "The external AI service is temporarily "
                "unavailable or has reached its usage limit."
            )

        elif error_name == "ServerError":
            message = (
                "The external AI service is temporarily "
                "unavailable. Please try again later."
            )

        else:
            message = (
                "An unexpected error occurred while processing "
                "the request."
            )

        return {
            "success": False,
            "error": "REQUEST_FAILED",
            "message": message
        }
        
        