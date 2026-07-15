"""Consents API - consents operation module: Obter detalhes de extensões feitas no consentimento identificado por consentId."""

from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from clients.consents_v3_3_1.client import AuthenticatedClient, Client
from clients.consents_v3_3_1.models.consents_get_consents_consent_id_extensions_response_529 import (
    ConsentsGetConsentsConsentIdExtensionsResponse529,
)
from clients.consents_v3_3_1.models.response_consent_read_extensions import ResponseConsentReadExtensions
from clients.consents_v3_3_1.models.response_error import ResponseError
from clients.consents_v3_3_1.types import UNSET, Response, Unset


def _get_kwargs(
    consent_id: str,
    *,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Authorization"] = authorization

    if not isinstance(x_fapi_auth_date, Unset):
        headers["x-fapi-auth-date"] = x_fapi_auth_date

    if not isinstance(x_fapi_customer_ip_address, Unset):
        headers["x-fapi-customer-ip-address"] = x_fapi_customer_ip_address

    headers["x-fapi-interaction-id"] = x_fapi_interaction_id

    if not isinstance(x_customer_user_agent, Unset):
        headers["x-customer-user-agent"] = x_customer_user_agent

    params: dict[str, Any] = {}

    params["page"] = page

    params["page-size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/consents/{consent_id}/extensions".format(
            consent_id=quote(str(consent_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    ConsentsGetConsentsConsentIdExtensionsResponse529
    | ResponseConsentReadExtensions
    | ResponseError
):
    if response.status_code == 200:
        response_200 = ResponseConsentReadExtensions.from_dict(response.json())

        return response_200

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
        response_529 = ConsentsGetConsentsConsentIdExtensionsResponse529.from_dict(
            response.json()
        )

        return response_529

    response_default = ResponseError.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    ConsentsGetConsentsConsentIdExtensionsResponse529
    | ResponseConsentReadExtensions
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
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[
    ConsentsGetConsentsConsentIdExtensionsResponse529
    | ResponseConsentReadExtensions
    | ResponseError
]:
    """Obter detalhes de extensões feitas no consentimento identificado por consentId.

     Método para obter histórico de extensões de consentimento identificado por consentId.

    IMPORTANTE: A lista do payload de resposta deve ser entregue em ordem decrescente pela data de
    requisição (`data[].requestDateTime`).
    Dessa forma, o primeiro item da lista apresentará a mesma data de expiração do consentimento
    vigente, pois foi a última renovação feita.

    Args:
        consent_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConsentsGetConsentsConsentIdExtensionsResponse529 | ResponseConsentReadExtensions | ResponseError]
    """

    kwargs = _get_kwargs(
        consent_id=consent_id,
        page=page,
        page_size=page_size,
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
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> (
    ConsentsGetConsentsConsentIdExtensionsResponse529
    | ResponseConsentReadExtensions
    | ResponseError
    | None
):
    """Obter detalhes de extensões feitas no consentimento identificado por consentId.

     Método para obter histórico de extensões de consentimento identificado por consentId.

    IMPORTANTE: A lista do payload de resposta deve ser entregue em ordem decrescente pela data de
    requisição (`data[].requestDateTime`).
    Dessa forma, o primeiro item da lista apresentará a mesma data de expiração do consentimento
    vigente, pois foi a última renovação feita.

    Args:
        consent_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConsentsGetConsentsConsentIdExtensionsResponse529 | ResponseConsentReadExtensions | ResponseError
    """

    return sync_detailed(
        consent_id=consent_id,
        client=client,
        page=page,
        page_size=page_size,
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
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[
    ConsentsGetConsentsConsentIdExtensionsResponse529
    | ResponseConsentReadExtensions
    | ResponseError
]:
    """Obter detalhes de extensões feitas no consentimento identificado por consentId.

     Método para obter histórico de extensões de consentimento identificado por consentId.

    IMPORTANTE: A lista do payload de resposta deve ser entregue em ordem decrescente pela data de
    requisição (`data[].requestDateTime`).
    Dessa forma, o primeiro item da lista apresentará a mesma data de expiração do consentimento
    vigente, pois foi a última renovação feita.

    Args:
        consent_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConsentsGetConsentsConsentIdExtensionsResponse529 | ResponseConsentReadExtensions | ResponseError]
    """

    kwargs = _get_kwargs(
        consent_id=consent_id,
        page=page,
        page_size=page_size,
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
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> (
    ConsentsGetConsentsConsentIdExtensionsResponse529
    | ResponseConsentReadExtensions
    | ResponseError
    | None
):
    """Obter detalhes de extensões feitas no consentimento identificado por consentId.

     Método para obter histórico de extensões de consentimento identificado por consentId.

    IMPORTANTE: A lista do payload de resposta deve ser entregue em ordem decrescente pela data de
    requisição (`data[].requestDateTime`).
    Dessa forma, o primeiro item da lista apresentará a mesma data de expiração do consentimento
    vigente, pois foi a última renovação feita.

    Args:
        consent_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConsentsGetConsentsConsentIdExtensionsResponse529 | ResponseConsentReadExtensions | ResponseError
    """

    return (
        await asyncio_detailed(
            consent_id=consent_id,
            client=client,
            page=page,
            page_size=page_size,
            authorization=authorization,
            x_fapi_auth_date=x_fapi_auth_date,
            x_fapi_customer_ip_address=x_fapi_customer_ip_address,
            x_fapi_interaction_id=x_fapi_interaction_id,
            x_customer_user_agent=x_customer_user_agent,
        )
    ).parsed
