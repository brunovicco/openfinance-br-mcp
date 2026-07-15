"""Accounts API - accounts operation module: Obtém os limites da conta identificada por accountId."""

from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from clients.accounts_v2_4_2.client import AuthenticatedClient, Client
from clients.accounts_v2_4_2.models.response_account_overdraft_limits import ResponseAccountOverdraftLimits
from clients.accounts_v2_4_2.models.response_error import ResponseError
from clients.accounts_v2_4_2.types import UNSET, Response, Unset


def _get_kwargs(
    account_id: str,
    *,
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

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/accounts/{account_id}/overdraft-limits".format(
            account_id=quote(str(account_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ResponseAccountOverdraftLimits | ResponseError:
    if response.status_code == 200:
        response_200 = ResponseAccountOverdraftLimits.from_dict(response.json())

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

    if response.status_code == 422:
        response_422 = ResponseError.from_dict(response.json())

        return response_422

    if response.status_code == 423:
        response_423 = ResponseError.from_dict(response.json())

        return response_423

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
        response_529 = ResponseError.from_dict(response.json())

        return response_529

    response_default = ResponseError.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ResponseAccountOverdraftLimits | ResponseError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_id: str,
    *,
    client: AuthenticatedClient,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[ResponseAccountOverdraftLimits | ResponseError]:
    """Obtém os limites da conta identificada por accountId.

     Método para obter os limites da conta de depósito à vista, poupança ou pagamento pré-paga
    identificada por accountId mantida pelo cliente na instituição transmissora. Para as instituições
    financeiras transmissoras que possuam contas sem limites associados devem retornar HTTP Status 200
    com o objeto “data” vazio, sem nenhum atributo interno.

    Args:
        account_id (str):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseAccountOverdraftLimits | ResponseError]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
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
    account_id: str,
    *,
    client: AuthenticatedClient,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> ResponseAccountOverdraftLimits | ResponseError | None:
    """Obtém os limites da conta identificada por accountId.

     Método para obter os limites da conta de depósito à vista, poupança ou pagamento pré-paga
    identificada por accountId mantida pelo cliente na instituição transmissora. Para as instituições
    financeiras transmissoras que possuam contas sem limites associados devem retornar HTTP Status 200
    com o objeto “data” vazio, sem nenhum atributo interno.

    Args:
        account_id (str):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseAccountOverdraftLimits | ResponseError
    """

    return sync_detailed(
        account_id=account_id,
        client=client,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    *,
    client: AuthenticatedClient,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[ResponseAccountOverdraftLimits | ResponseError]:
    """Obtém os limites da conta identificada por accountId.

     Método para obter os limites da conta de depósito à vista, poupança ou pagamento pré-paga
    identificada por accountId mantida pelo cliente na instituição transmissora. Para as instituições
    financeiras transmissoras que possuam contas sem limites associados devem retornar HTTP Status 200
    com o objeto “data” vazio, sem nenhum atributo interno.

    Args:
        account_id (str):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseAccountOverdraftLimits | ResponseError]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    *,
    client: AuthenticatedClient,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> ResponseAccountOverdraftLimits | ResponseError | None:
    """Obtém os limites da conta identificada por accountId.

     Método para obter os limites da conta de depósito à vista, poupança ou pagamento pré-paga
    identificada por accountId mantida pelo cliente na instituição transmissora. Para as instituições
    financeiras transmissoras que possuam contas sem limites associados devem retornar HTTP Status 200
    com o objeto “data” vazio, sem nenhum atributo interno.

    Args:
        account_id (str):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseAccountOverdraftLimits | ResponseError
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            client=client,
            authorization=authorization,
            x_fapi_auth_date=x_fapi_auth_date,
            x_fapi_customer_ip_address=x_fapi_customer_ip_address,
            x_fapi_interaction_id=x_fapi_interaction_id,
            x_customer_user_agent=x_customer_user_agent,
        )
    ).parsed
