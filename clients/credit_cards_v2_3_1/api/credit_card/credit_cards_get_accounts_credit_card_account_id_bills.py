"""Credit Cards Accounts API - credit_card operation module: Obtém a lista de faturas da conta identificada por creditCardAccountId."""

import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from clients.credit_cards_v2_3_1.client import AuthenticatedClient, Client
from clients.credit_cards_v2_3_1.models.response_credit_card_accounts_bills import (
    ResponseCreditCardAccountsBills,
)
from clients.credit_cards_v2_3_1.models.response_error import ResponseError
from clients.credit_cards_v2_3_1.types import UNSET, Response, Unset


def _get_kwargs(
    credit_card_account_id: str,
    *,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_due_date: datetime.date | Unset = UNSET,
    to_due_date: datetime.date | Unset = UNSET,
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

    params["pagination-key"] = pagination_key

    json_from_due_date: str | Unset = UNSET
    if not isinstance(from_due_date, Unset):
        json_from_due_date = from_due_date.isoformat()
    params["fromDueDate"] = json_from_due_date

    json_to_due_date: str | Unset = UNSET
    if not isinstance(to_due_date, Unset):
        json_to_due_date = to_due_date.isoformat()
    params["toDueDate"] = json_to_due_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/accounts/{credit_card_account_id}/bills".format(
            credit_card_account_id=quote(str(credit_card_account_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ResponseCreditCardAccountsBills | ResponseError:
    if response.status_code == 200:
        response_200 = ResponseCreditCardAccountsBills.from_dict(response.json())

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
) -> Response[ResponseCreditCardAccountsBills | ResponseError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    credit_card_account_id: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_due_date: datetime.date | Unset = UNSET,
    to_due_date: datetime.date | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[ResponseCreditCardAccountsBills | ResponseError]:
    r""" Obtém a lista de faturas da conta identificada por creditCardAccountId.

     Método para obter a lista de faturas da conta de pagamento pós-paga identificada por
    creditCardAccountId mantida pelo cliente na instituição transmissora.\
    Só deve ser informada uma fatura já fechada.\
    Qualquer pagamento deve ser contado para a última fatura fechada.

    Args:
        credit_card_account_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        pagination_key (str | Unset):
        from_due_date (datetime.date | Unset):  Example: 2021-05-21.
        to_due_date (datetime.date | Unset):  Example: 2021-05-21.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseCreditCardAccountsBills | ResponseError]
     """

    kwargs = _get_kwargs(
        credit_card_account_id=credit_card_account_id,
        page=page,
        page_size=page_size,
        pagination_key=pagination_key,
        from_due_date=from_due_date,
        to_due_date=to_due_date,
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
    credit_card_account_id: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_due_date: datetime.date | Unset = UNSET,
    to_due_date: datetime.date | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> ResponseCreditCardAccountsBills | ResponseError | None:
    r""" Obtém a lista de faturas da conta identificada por creditCardAccountId.

     Método para obter a lista de faturas da conta de pagamento pós-paga identificada por
    creditCardAccountId mantida pelo cliente na instituição transmissora.\
    Só deve ser informada uma fatura já fechada.\
    Qualquer pagamento deve ser contado para a última fatura fechada.

    Args:
        credit_card_account_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        pagination_key (str | Unset):
        from_due_date (datetime.date | Unset):  Example: 2021-05-21.
        to_due_date (datetime.date | Unset):  Example: 2021-05-21.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseCreditCardAccountsBills | ResponseError
     """

    return sync_detailed(
        credit_card_account_id=credit_card_account_id,
        client=client,
        page=page,
        page_size=page_size,
        pagination_key=pagination_key,
        from_due_date=from_due_date,
        to_due_date=to_due_date,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    ).parsed


async def asyncio_detailed(
    credit_card_account_id: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_due_date: datetime.date | Unset = UNSET,
    to_due_date: datetime.date | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[ResponseCreditCardAccountsBills | ResponseError]:
    r""" Obtém a lista de faturas da conta identificada por creditCardAccountId.

     Método para obter a lista de faturas da conta de pagamento pós-paga identificada por
    creditCardAccountId mantida pelo cliente na instituição transmissora.\
    Só deve ser informada uma fatura já fechada.\
    Qualquer pagamento deve ser contado para a última fatura fechada.

    Args:
        credit_card_account_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        pagination_key (str | Unset):
        from_due_date (datetime.date | Unset):  Example: 2021-05-21.
        to_due_date (datetime.date | Unset):  Example: 2021-05-21.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseCreditCardAccountsBills | ResponseError]
     """

    kwargs = _get_kwargs(
        credit_card_account_id=credit_card_account_id,
        page=page,
        page_size=page_size,
        pagination_key=pagination_key,
        from_due_date=from_due_date,
        to_due_date=to_due_date,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    credit_card_account_id: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_due_date: datetime.date | Unset = UNSET,
    to_due_date: datetime.date | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> ResponseCreditCardAccountsBills | ResponseError | None:
    r""" Obtém a lista de faturas da conta identificada por creditCardAccountId.

     Método para obter a lista de faturas da conta de pagamento pós-paga identificada por
    creditCardAccountId mantida pelo cliente na instituição transmissora.\
    Só deve ser informada uma fatura já fechada.\
    Qualquer pagamento deve ser contado para a última fatura fechada.

    Args:
        credit_card_account_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        pagination_key (str | Unset):
        from_due_date (datetime.date | Unset):  Example: 2021-05-21.
        to_due_date (datetime.date | Unset):  Example: 2021-05-21.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseCreditCardAccountsBills | ResponseError
     """

    return (
        await asyncio_detailed(
            credit_card_account_id=credit_card_account_id,
            client=client,
            page=page,
            page_size=page_size,
            pagination_key=pagination_key,
            from_due_date=from_due_date,
            to_due_date=to_due_date,
            authorization=authorization,
            x_fapi_auth_date=x_fapi_auth_date,
            x_fapi_customer_ip_address=x_fapi_customer_ip_address,
            x_fapi_interaction_id=x_fapi_interaction_id,
            x_customer_user_agent=x_customer_user_agent,
        )
    ).parsed
