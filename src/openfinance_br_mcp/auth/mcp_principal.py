"""Stable identity derivation for authenticated MCP callers.

OAuth ``client_id`` identifies an application, not the resource owner using
that application. Financial subject bindings therefore use the verified
issuer and subject claims and reject tokens that cannot identify a user.
"""

from mcp.server.auth.provider import AccessToken

from openfinance_br_mcp.exceptions import ValidationError


def principal_from_access_token(access_token: AccessToken) -> str:
    """Returns the canonical ``issuer::subject`` MCP principal.

    Raises:
        ValidationError: If the verified token has no issuer or subject.
    """
    claims = access_token.claims or {}
    issuer = claims.get("iss")
    subject = access_token.subject or claims.get("sub")
    if not isinstance(issuer, str) or not issuer:
        raise ValidationError(
            "The authenticated MCP token has no issuer claim.",
            code="MCP_PRINCIPAL_ISSUER_REQUIRED",
        )
    if not isinstance(subject, str) or not subject:
        raise ValidationError(
            "The authenticated MCP token has no subject claim; financial "
            "operations require a user-bound token.",
            code="MCP_PRINCIPAL_SUBJECT_REQUIRED",
        )
    return f"{issuer}::{subject}"
