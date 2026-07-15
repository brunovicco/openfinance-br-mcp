"""Variable Incomes API - transactions_current operation module: Obtém as movimentações recentes da operação de Renda Variável identificada por investmentId. O"""

import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from clients.variable_incomes_v1_3_0.client import AuthenticatedClient, Client
from clients.variable_incomes_v1_3_0.models.response_error_meta_single import ResponseErrorMetaSingle
from clients.variable_incomes_v1_3_0.models.response_variable_incomes_transactions_current import (
    ResponseVariableIncomesTransactionsCurrent,
)
from clients.variable_incomes_v1_3_0.models.variable_incomes_get_investments_investment_id_transactions_current_response_423 import (
    VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423,
)
from clients.variable_incomes_v1_3_0.types import UNSET, Response, Unset


def _get_kwargs(
    investment_id: str,
    *,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_transaction_date: datetime.date | Unset = UNSET,
    to_transaction_date: datetime.date | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: str,
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

    json_from_transaction_date: str | Unset = UNSET
    if not isinstance(from_transaction_date, Unset):
        json_from_transaction_date = from_transaction_date.isoformat()
    params["fromTransactionDate"] = json_from_transaction_date

    json_to_transaction_date: str | Unset = UNSET
    if not isinstance(to_transaction_date, Unset):
        json_to_transaction_date = to_transaction_date.isoformat()
    params["toTransactionDate"] = json_to_transaction_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/investments/{investment_id}/transactions-current".format(
            investment_id=quote(str(investment_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    ResponseErrorMetaSingle
    | ResponseVariableIncomesTransactionsCurrent
    | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423
):
    if response.status_code == 200:
        response_200 = ResponseVariableIncomesTransactionsCurrent.from_dict(
            response.json()
        )

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
        response_423 = VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423.from_dict(
            response.json()
        )

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
) -> Response[
    ResponseErrorMetaSingle
    | ResponseVariableIncomesTransactionsCurrent
    | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    investment_id: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_transaction_date: datetime.date | Unset = UNSET,
    to_transaction_date: datetime.date | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: str,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[
    ResponseErrorMetaSingle
    | ResponseVariableIncomesTransactionsCurrent
    | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423
]:
    """Obtém as movimentações recentes da operação de Renda Variável identificada por investmentId. O
    período a ser considerado para apresentação de movimentações será de até 7 dias - 7 dias anteriores
    da consulta, incluindo o dia da consulta (D-6).

     Obtém as movimentações recentes da operação de Renda Variável identificada por investmentId. O
    período a ser considerado para apresentação de movimentações será de até 7 dias - 7 dias anteriores
    da consulta, incluindo o dia da consulta (D-6).

    Args:
        investment_id (str):  Example: 92792126019929200000000000000000000000000.
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        pagination_key (str | Unset):
        from_transaction_date (datetime.date | Unset):  Example: 2023-02-01.
        to_transaction_date (datetime.date | Unset):  Example: 2023-02-01.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (str):
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseErrorMetaSingle | ResponseVariableIncomesTransactionsCurrent | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423]
    """

    kwargs = _get_kwargs(
        investment_id=investment_id,
        page=page,
        page_size=page_size,
        pagination_key=pagination_key,
        from_transaction_date=from_transaction_date,
        to_transaction_date=to_transaction_date,
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
    investment_id: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_transaction_date: datetime.date | Unset = UNSET,
    to_transaction_date: datetime.date | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: str,
    x_customer_user_agent: str | Unset = UNSET,
) -> (
    ResponseErrorMetaSingle
    | ResponseVariableIncomesTransactionsCurrent
    | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423
    | None
):
    """Obtém as movimentações recentes da operação de Renda Variável identificada por investmentId. O
    período a ser considerado para apresentação de movimentações será de até 7 dias - 7 dias anteriores
    da consulta, incluindo o dia da consulta (D-6).

     Obtém as movimentações recentes da operação de Renda Variável identificada por investmentId. O
    período a ser considerado para apresentação de movimentações será de até 7 dias - 7 dias anteriores
    da consulta, incluindo o dia da consulta (D-6).

    Args:
        investment_id (str):  Example: 92792126019929200000000000000000000000000.
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        pagination_key (str | Unset):
        from_transaction_date (datetime.date | Unset):  Example: 2023-02-01.
        to_transaction_date (datetime.date | Unset):  Example: 2023-02-01.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (str):
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseErrorMetaSingle | ResponseVariableIncomesTransactionsCurrent | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423
    """

    return sync_detailed(
        investment_id=investment_id,
        client=client,
        page=page,
        page_size=page_size,
        pagination_key=pagination_key,
        from_transaction_date=from_transaction_date,
        to_transaction_date=to_transaction_date,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    ).parsed


async def asyncio_detailed(
    investment_id: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_transaction_date: datetime.date | Unset = UNSET,
    to_transaction_date: datetime.date | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: str,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[
    ResponseErrorMetaSingle
    | ResponseVariableIncomesTransactionsCurrent
    | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423
]:
    """Obtém as movimentações recentes da operação de Renda Variável identificada por investmentId. O
    período a ser considerado para apresentação de movimentações será de até 7 dias - 7 dias anteriores
    da consulta, incluindo o dia da consulta (D-6).

     Obtém as movimentações recentes da operação de Renda Variável identificada por investmentId. O
    período a ser considerado para apresentação de movimentações será de até 7 dias - 7 dias anteriores
    da consulta, incluindo o dia da consulta (D-6).

    Args:
        investment_id (str):  Example: 92792126019929200000000000000000000000000.
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        pagination_key (str | Unset):
        from_transaction_date (datetime.date | Unset):  Example: 2023-02-01.
        to_transaction_date (datetime.date | Unset):  Example: 2023-02-01.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (str):
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseErrorMetaSingle | ResponseVariableIncomesTransactionsCurrent | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423]
    """

    kwargs = _get_kwargs(
        investment_id=investment_id,
        page=page,
        page_size=page_size,
        pagination_key=pagination_key,
        from_transaction_date=from_transaction_date,
        to_transaction_date=to_transaction_date,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    investment_id: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    pagination_key: str | Unset = UNSET,
    from_transaction_date: datetime.date | Unset = UNSET,
    to_transaction_date: datetime.date | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: str,
    x_customer_user_agent: str | Unset = UNSET,
) -> (
    ResponseErrorMetaSingle
    | ResponseVariableIncomesTransactionsCurrent
    | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423
    | None
):
    """Obtém as movimentações recentes da operação de Renda Variável identificada por investmentId. O
    período a ser considerado para apresentação de movimentações será de até 7 dias - 7 dias anteriores
    da consulta, incluindo o dia da consulta (D-6).

     Obtém as movimentações recentes da operação de Renda Variável identificada por investmentId. O
    período a ser considerado para apresentação de movimentações será de até 7 dias - 7 dias anteriores
    da consulta, incluindo o dia da consulta (D-6).

    Args:
        investment_id (str):  Example: 92792126019929200000000000000000000000000.
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        pagination_key (str | Unset):
        from_transaction_date (datetime.date | Unset):  Example: 2023-02-01.
        to_transaction_date (datetime.date | Unset):  Example: 2023-02-01.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (str):
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseErrorMetaSingle | ResponseVariableIncomesTransactionsCurrent | VariableIncomesGetInvestmentsInvestmentIdTransactionsCurrentResponse423
    """

    return (
        await asyncio_detailed(
            investment_id=investment_id,
            client=client,
            page=page,
            page_size=page_size,
            pagination_key=pagination_key,
            from_transaction_date=from_transaction_date,
            to_transaction_date=to_transaction_date,
            authorization=authorization,
            x_fapi_auth_date=x_fapi_auth_date,
            x_fapi_customer_ip_address=x_fapi_customer_ip_address,
            x_fapi_interaction_id=x_fapi_interaction_id,
            x_customer_user_agent=x_customer_user_agent,
        )
    ).parsed
