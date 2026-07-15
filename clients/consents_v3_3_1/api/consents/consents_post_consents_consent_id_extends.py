"""Consents API - consents operation module: Renovar consentimento identificado por consentId."""

from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from clients.consents_v3_3_1.client import AuthenticatedClient, Client
from clients.consents_v3_3_1.models.consents_post_consents_consent_id_extends_response_529 import (
    ConsentsPostConsentsConsentIdExtendsResponse529,
)
from clients.consents_v3_3_1.models.create_consent_extensions import CreateConsentExtensions
from clients.consents_v3_3_1.models.field_422_response_error_create_consent import (
    Field422ResponseErrorCreateConsent,
)
from clients.consents_v3_3_1.models.response_consent_extensions import ResponseConsentExtensions
from clients.consents_v3_3_1.models.response_error import ResponseError
from clients.consents_v3_3_1.types import UNSET, Response, Unset


def _get_kwargs(
    consent_id: str,
    *,
    body: CreateConsentExtensions,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Authorization"] = authorization

    if not isinstance(x_fapi_auth_date, Unset):
        headers["x-fapi-auth-date"] = x_fapi_auth_date

    headers["x-fapi-customer-ip-address"] = x_fapi_customer_ip_address

    headers["x-fapi-interaction-id"] = x_fapi_interaction_id

    headers["x-customer-user-agent"] = x_customer_user_agent

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/consents/{consent_id}/extends".format(
            consent_id=quote(str(consent_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    ConsentsPostConsentsConsentIdExtendsResponse529
    | Field422ResponseErrorCreateConsent
    | ResponseConsentExtensions
    | ResponseError
):
    if response.status_code == 201:
        response_201 = ResponseConsentExtensions.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = ResponseError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = ResponseError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ResponseError.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ResponseError.from_dict(response.json())

        return response_404

    if response.status_code == 405:
        response_405 = ResponseError.from_dict(response.json())

        return response_405

    if response.status_code == 406:
        response_406 = ResponseError.from_dict(response.json())

        return response_406

    if response.status_code == 415:
        response_415 = ResponseError.from_dict(response.json())

        return response_415

    if response.status_code == 422:
        response_422 = Field422ResponseErrorCreateConsent.from_dict(response.json())

        return response_422

    if response.status_code == 429:
        response_429 = ResponseError.from_dict(response.json())

        return response_429

    if response.status_code == 500:
        response_500 = ResponseError.from_dict(response.json())

        return response_500

    if response.status_code == 504:
        response_504 = ResponseError.from_dict(response.json())

        return response_504

    if response.status_code == 529:
        response_529 = ConsentsPostConsentsConsentIdExtendsResponse529.from_dict(
            response.json()
        )

        return response_529

    response_default = ResponseError.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    ConsentsPostConsentsConsentIdExtendsResponse529
    | Field422ResponseErrorCreateConsent
    | ResponseConsentExtensions
    | ResponseError
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    consent_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateConsentExtensions,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str,
) -> Response[
    ConsentsPostConsentsConsentIdExtendsResponse529
    | Field422ResponseErrorCreateConsent
    | ResponseConsentExtensions
    | ResponseError
]:
    """Renovar consentimento identificado por consentId.

     Método utilizado para renovação de consentimento do cliente. O consentimento só pode ser renovado
    caso esteja ativo (status AUTHORISED) e tenha alçada simples de aprovação (não dependa de múltiplos
    aprovadores).  A alteração de data efetuada pela renovação deve ser refletida também na consulta do
    método _GET/consents/{consentId}_.

    Args:
        consent_id (str):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str):
        body (CreateConsentExtensions):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConsentsPostConsentsConsentIdExtendsResponse529 | Field422ResponseErrorCreateConsent | ResponseConsentExtensions | ResponseError]
    """

    kwargs = _get_kwargs(
        consent_id=consent_id,
        body=body,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    consent_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateConsentExtensions,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str,
) -> (
    ConsentsPostConsentsConsentIdExtendsResponse529
    | Field422ResponseErrorCreateConsent
    | ResponseConsentExtensions
    | ResponseError
    | None
):
    """Renovar consentimento identificado por consentId.

     Método utilizado para renovação de consentimento do cliente. O consentimento só pode ser renovado
    caso esteja ativo (status AUTHORISED) e tenha alçada simples de aprovação (não dependa de múltiplos
    aprovadores).  A alteração de data efetuada pela renovação deve ser refletida também na consulta do
    método _GET/consents/{consentId}_.

    Args:
        consent_id (str):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str):
        body (CreateConsentExtensions):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConsentsPostConsentsConsentIdExtendsResponse529 | Field422ResponseErrorCreateConsent | ResponseConsentExtensions | ResponseError
    """

    return sync_detailed(
        consent_id=consent_id,
        client=client,
        body=body,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    ).parsed


async def asyncio_detailed(
    consent_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateConsentExtensions,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str,
) -> Response[
    ConsentsPostConsentsConsentIdExtendsResponse529
    | Field422ResponseErrorCreateConsent
    | ResponseConsentExtensions
    | ResponseError
]:
    """Renovar consentimento identificado por consentId.

     Método utilizado para renovação de consentimento do cliente. O consentimento só pode ser renovado
    caso esteja ativo (status AUTHORISED) e tenha alçada simples de aprovação (não dependa de múltiplos
    aprovadores).  A alteração de data efetuada pela renovação deve ser refletida também na consulta do
    método _GET/consents/{consentId}_.

    Args:
        consent_id (str):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str):
        body (CreateConsentExtensions):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConsentsPostConsentsConsentIdExtendsResponse529 | Field422ResponseErrorCreateConsent | ResponseConsentExtensions | ResponseError]
    """

    kwargs = _get_kwargs(
        consent_id=consent_id,
        body=body,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    consent_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateConsentExtensions,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str,
) -> (
    ConsentsPostConsentsConsentIdExtendsResponse529
    | Field422ResponseErrorCreateConsent
    | ResponseConsentExtensions
    | ResponseError
    | None
):
    """Renovar consentimento identificado por consentId.

     Método utilizado para renovação de consentimento do cliente. O consentimento só pode ser renovado
    caso esteja ativo (status AUTHORISED) e tenha alçada simples de aprovação (não dependa de múltiplos
    aprovadores).  A alteração de data efetuada pela renovação deve ser refletida também na consulta do
    método _GET/consents/{consentId}_.

    Args:
        consent_id (str):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str):
        body (CreateConsentExtensions):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConsentsPostConsentsConsentIdExtendsResponse529 | Field422ResponseErrorCreateConsent | ResponseConsentExtensions | ResponseError
    """

    return (
        await asyncio_detailed(
            consent_id=consent_id,
            client=client,
            body=body,
            authorization=authorization,
            x_fapi_auth_date=x_fapi_auth_date,
            x_fapi_customer_ip_address=x_fapi_customer_ip_address,
            x_fapi_interaction_id=x_fapi_interaction_id,
            x_customer_user_agent=x_customer_user_agent,
        )
    ).parsed
