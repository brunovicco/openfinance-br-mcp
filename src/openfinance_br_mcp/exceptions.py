"""Exception hierarchy for the openfinance-br-mcp domain.

Defines all custom exceptions following the single-responsibility
principle: each error class represents a specific, traceable failure
case.

Example:
    >>> raise ConsentExpiredError("Consent abc123 has expired")
    ConsentExpiredError: Consent abc123 has expired
"""


class OpenFinanceError(Exception):
    """Base exception for all errors in the Open Finance domain.

    Attributes:
        message: Human-readable description of the error.
        code: Optional error code for traceability.
    """

    def __init__(self, message: str, code: str | None = None) -> None:
        """Initializes the exception with a message and optional code.

        Args:
            message: Description of the error.
            code: Error code for traceability (e.g. 'OF_001').
        """
        super().__init__(message)
        self.message = message
        self.code = code


class AuthenticationError(OpenFinanceError):
    """Failure in the OAuth2/FAPI authentication or authorization process."""


class ConsentError(OpenFinanceError):
    """Error related to the consent lifecycle."""


class ConsentExpiredError(ConsentError):
    """The consent has expired and needs to be renewed."""


class ConsentDeniedError(ConsentError):
    """The user denied consent at the bank."""


class TokenError(OpenFinanceError):
    """Error managing or refreshing tokens."""


class TokenRefreshError(TokenError):
    """Failed to refresh the access token via the refresh token."""


class BankAdapterError(OpenFinanceError):
    """Error originating from a specific bank adapter.

    Attributes:
        bank_id: Identifier of the bank that raised the error.
        status_code: HTTP status code returned by the bank, if available.
    """

    def __init__(
        self,
        message: str,
        bank_id: str,
        status_code: int | None = None,
        code: str | None = None,
    ) -> None:
        """Initializes with the bank identifier and HTTP status.

        Args:
            message: Description of the error.
            bank_id: ISPB code or name of the bank.
            status_code: HTTP status code returned by the bank.
            code: Internal traceability code.
        """
        super().__init__(message, code)
        self.bank_id = bank_id
        self.status_code = status_code


class RateLimitError(BankAdapterError):
    """The bank returned HTTP 429 - request rate limit exceeded."""


class ResourceNotFoundError(BankAdapterError):
    """The requested resource was not found at the bank (HTTP 404)."""


class ValidationError(OpenFinanceError):
    """Validation error in a tool's input parameters."""


class SchemaError(OpenFinanceError):
    """Failed to parse/validate a bank's API response."""


class CategorizationError(OpenFinanceError):
    """Error in the DSPy transaction categorization module."""


class DirectoryError(OpenFinanceError):
    """Error resolving a bank's endpoints via the Directory of Participants.

    Attributes:
        bank_id: Identifier of the bank being resolved, if known.
    """

    def __init__(
        self,
        message: str,
        bank_id: str | None = None,
        code: str | None = None,
    ) -> None:
        """Initializes with the bank identifier being resolved.

        Args:
            message: Description of the error.
            bank_id: Identifier of the bank being resolved.
            code: Internal traceability code.
        """
        super().__init__(message, code)
        self.bank_id = bank_id
