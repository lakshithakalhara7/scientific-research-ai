import re


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