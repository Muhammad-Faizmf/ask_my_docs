from google.genai.errors import APIError
from groq import APIStatusError


def model_service_message(error: Exception, operation: str) -> str | None:
    """Return a user-facing message for a model provider capacity error."""
    while error is not None:
        if isinstance(error, APIStatusError):
            status_code = error.status_code
            quota_exhausted = status_code == 429
        elif isinstance(error, APIError):
            status_code = error.code
            quota_exhausted = status_code == 429 or error.status == "RESOURCE_EXHAUSTED"
        else:
            status_code = None
            quota_exhausted = False

        if quota_exhausted:
            return (
                f"The AI service reached its usage limit and couldn't {operation}. "
                "Please try again later."
            )
        if status_code == 503:
            return (
                f"The AI service is temporarily unavailable and couldn't {operation}. "
                "Please try again later."
            )

        error = error.__cause__ or error.__context__

    return None
