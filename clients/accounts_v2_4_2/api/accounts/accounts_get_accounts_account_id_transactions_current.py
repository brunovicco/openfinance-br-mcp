"""Accounts API - accounts operation module: Obtém a lista de transações recentes (últimos 7 dias) da conta identificada por accountId."""

import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from clients.accounts_v2_4_2.client import AuthenticatedClient, Client
from clients.accounts_v2_4_2.models.enum_credit_debit_indicator import EnumCreditDebitIndicator
from clients.accounts_v2_4_2.models.response_account_transactions import ResponseAccountTransactions
from clients.accounts_v2_4_2.models.response_error_meta_single import ResponseErrorMetaSingle
from clients.accounts_v2_4_2.types import UNSET, Response, Unset


def _get_kwargs(
    account_id: str,
    *,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    from_booking_date: datetime.date | Unset = UNSET,
    to_booking_date: datetime.date | Unset = UNSET,
    credit_debit_indicator: EnumCreditDebitIndicator | Unset = UNSET,
    pagination_key: str | Unset = UNSET,
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

    json_from_booking_date: str | Unset = UNSET
    if not isinstance(from_booking_date, Unset):
        json_from_booking_date = from_booking_date.isoformat()
    params["fromBookingDate"] = json_from_booking_date

    json_to_booking_date: str | Unset = UNSET
    if not isinstance(to_booking_date, Unset):
        json_to_booking_date = to_booking_date.isoformat()
    params["toBookingDate"] = json_to_booking_date

    json_credit_debit_indicator: str | Unset = UNSET
    if not isinstance(credit_debit_indicator, Unset):
        json_credit_debit_indicator = credit_debit_indicator.value

    params["creditDebitIndicator"] = json_credit_debit_indicator

    params["pagination-key"] = pagination_key

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/accounts/{account_id}/transactions-current".format(
            account_id=quote(str(account_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ResponseAccountTransactions | ResponseErrorMetaSingle:
    if response.status_code == 200:
        response_200 = ResponseAccountTransactions.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_404

    if response.status_code == 405:
        response_405 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_405

    if response.status_code == 406:
        response_406 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_406

    if response.status_code == 422:
        response_422 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_422

    if response.status_code == 423:
        response_423 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_423

    if response.status_code == 429:
        response_429 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_429

    if response.status_code == 500:
        response_500 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_500

    if response.status_code == 504:
        response_504 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_504

    if response.status_code == 529:
        response_529 = ResponseErrorMetaSingle.from_dict(response.json())

        return response_529

    response_default = ResponseErrorMetaSingle.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ResponseAccountTransactions | ResponseErrorMetaSingle]:
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
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    from_booking_date: datetime.date | Unset = UNSET,
    to_booking_date: datetime.date | Unset = UNSET,
    credit_debit_indicator: EnumCreditDebitIndicator | Unset = UNSET,
    pagination_key: str | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[ResponseAccountTransactions | ResponseErrorMetaSingle]:
    """Obtém a lista de transações recentes (últimos 7 dias) da conta identificada por accountId.

     Método para obter a lista de transações da conta de depósito à vista, poupança ou pagamento pré-paga
    identificada por accountId mantida pelo cliente na instituição transmissora. É permitida uma
    consulta máxima que se estenda em 7 dias no passado mais 12 meses no futuro.

    Args:
        account_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        from_booking_date (datetime.date | Unset):  Example: 2021-05-21.
        to_booking_date (datetime.date | Unset):  Example: 2021-05-21.
        credit_debit_indicator (EnumCreditDebitIndicator | Unset): Indicador do tipo de
            lançamento:
            Débito (no extrato) Em um extrato bancário, os débitos, marcados com a letra “D” ao lado
            do valor registrado, informam as saídas de dinheiro na conta-corrente.
            Crédito (no extrato) Em um extrato bancário, os créditos, marcados com a letra “C” ao lado
            do valor registrado, informam as entradas de dinheiro na conta-corrente.
             Example: DEBITO.
        pagination_key (str | Unset):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseAccountTransactions | ResponseErrorMetaSingle]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        page=page,
        page_size=page_size,
        from_booking_date=from_booking_date,
        to_booking_date=to_booking_date,
        credit_debit_indicator=credit_debit_indicator,
        pagination_key=pagination_key,
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
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    from_booking_date: datetime.date | Unset = UNSET,
    to_booking_date: datetime.date | Unset = UNSET,
    credit_debit_indicator: EnumCreditDebitIndicator | Unset = UNSET,
    pagination_key: str | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> ResponseAccountTransactions | ResponseErrorMetaSingle | None:
    """Obtém a lista de transações recentes (últimos 7 dias) da conta identificada por accountId.

     Método para obter a lista de transações da conta de depósito à vista, poupança ou pagamento pré-paga
    identificada por accountId mantida pelo cliente na instituição transmissora. É permitida uma
    consulta máxima que se estenda em 7 dias no passado mais 12 meses no futuro.

    Args:
        account_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        from_booking_date (datetime.date | Unset):  Example: 2021-05-21.
        to_booking_date (datetime.date | Unset):  Example: 2021-05-21.
        credit_debit_indicator (EnumCreditDebitIndicator | Unset): Indicador do tipo de
            lançamento:
            Débito (no extrato) Em um extrato bancário, os débitos, marcados com a letra “D” ao lado
            do valor registrado, informam as saídas de dinheiro na conta-corrente.
            Crédito (no extrato) Em um extrato bancário, os créditos, marcados com a letra “C” ao lado
            do valor registrado, informam as entradas de dinheiro na conta-corrente.
             Example: DEBITO.
        pagination_key (str | Unset):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseAccountTransactions | ResponseErrorMetaSingle
    """

    return sync_detailed(
        account_id=account_id,
        client=client,
        page=page,
        page_size=page_size,
        from_booking_date=from_booking_date,
        to_booking_date=to_booking_date,
        credit_debit_indicator=credit_debit_indicator,
        pagination_key=pagination_key,
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
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    from_booking_date: datetime.date | Unset = UNSET,
    to_booking_date: datetime.date | Unset = UNSET,
    credit_debit_indicator: EnumCreditDebitIndicator | Unset = UNSET,
    pagination_key: str | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[ResponseAccountTransactions | ResponseErrorMetaSingle]:
    """Obtém a lista de transações recentes (últimos 7 dias) da conta identificada por accountId.

     Método para obter a lista de transações da conta de depósito à vista, poupança ou pagamento pré-paga
    identificada por accountId mantida pelo cliente na instituição transmissora. É permitida uma
    consulta máxima que se estenda em 7 dias no passado mais 12 meses no futuro.

    Args:
        account_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        from_booking_date (datetime.date | Unset):  Example: 2021-05-21.
        to_booking_date (datetime.date | Unset):  Example: 2021-05-21.
        credit_debit_indicator (EnumCreditDebitIndicator | Unset): Indicador do tipo de
            lançamento:
            Débito (no extrato) Em um extrato bancário, os débitos, marcados com a letra “D” ao lado
            do valor registrado, informam as saídas de dinheiro na conta-corrente.
            Crédito (no extrato) Em um extrato bancário, os créditos, marcados com a letra “C” ao lado
            do valor registrado, informam as entradas de dinheiro na conta-corrente.
             Example: DEBITO.
        pagination_key (str | Unset):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseAccountTransactions | ResponseErrorMetaSingle]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        page=page,
        page_size=page_size,
        from_booking_date=from_booking_date,
        to_booking_date=to_booking_date,
        credit_debit_indicator=credit_debit_indicator,
        pagination_key=pagination_key,
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
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    from_booking_date: datetime.date | Unset = UNSET,
    to_booking_date: datetime.date | Unset = UNSET,
    credit_debit_indicator: EnumCreditDebitIndicator | Unset = UNSET,
    pagination_key: str | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> ResponseAccountTransactions | ResponseErrorMetaSingle | None:
    """Obtém a lista de transações recentes (últimos 7 dias) da conta identificada por accountId.

     Método para obter a lista de transações da conta de depósito à vista, poupança ou pagamento pré-paga
    identificada por accountId mantida pelo cliente na instituição transmissora. É permitida uma
    consulta máxima que se estenda em 7 dias no passado mais 12 meses no futuro.

    Args:
        account_id (str):
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        from_booking_date (datetime.date | Unset):  Example: 2021-05-21.
        to_booking_date (datetime.date | Unset):  Example: 2021-05-21.
        credit_debit_indicator (EnumCreditDebitIndicator | Unset): Indicador do tipo de
            lançamento:
            Débito (no extrato) Em um extrato bancário, os débitos, marcados com a letra “D” ao lado
            do valor registrado, informam as saídas de dinheiro na conta-corrente.
            Crédito (no extrato) Em um extrato bancário, os créditos, marcados com a letra “C” ao lado
            do valor registrado, informam as entradas de dinheiro na conta-corrente.
             Example: DEBITO.
        pagination_key (str | Unset):
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (UUID):  Example: d78fc4e5-37ca-4da3-adf2-9b082bf92280.
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseAccountTransactions | ResponseErrorMetaSingle
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            client=client,
            page=page,
            page_size=page_size,
            from_booking_date=from_booking_date,
            to_booking_date=to_booking_date,
            credit_debit_indicator=credit_debit_indicator,
            pagination_key=pagination_key,
            authorization=authorization,
            x_fapi_auth_date=x_fapi_auth_date,
            x_fapi_customer_ip_address=x_fapi_customer_ip_address,
            x_fapi_interaction_id=x_fapi_interaction_id,
            x_customer_user_agent=x_customer_user_agent,
        )
    ).parsed
