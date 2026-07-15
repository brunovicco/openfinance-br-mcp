"""Variable Incomes API - broker_note_details operation module: Obtém as informações da nota de negociação identificado nas movimentações de compra e venda de"""

from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from clients.variable_incomes_v1_3_0.client import AuthenticatedClient, Client
from clients.variable_incomes_v1_3_0.models.response_error_meta_single import ResponseErrorMetaSingle
from clients.variable_incomes_v1_3_0.models.response_variable_incomes_broker import ResponseVariableIncomesBroker
from clients.variable_incomes_v1_3_0.models.variable_incomes_get_investments_investment_id_broker_notes_broker_note_id_response_423 import (
    VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423,
)
from clients.variable_incomes_v1_3_0.types import UNSET, Response, Unset


def _get_kwargs(
    broker_note_id: str,
    *,
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

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/broker-notes/{broker_note_id}".format(
            broker_note_id=quote(str(broker_note_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    ResponseErrorMetaSingle
    | ResponseVariableIncomesBroker
    | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423
):
    if response.status_code == 200:
        response_200 = ResponseVariableIncomesBroker.from_dict(response.json())

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
        response_423 = VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423.from_dict(
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
    | ResponseVariableIncomesBroker
    | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    broker_note_id: str,
    *,
    client: AuthenticatedClient,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: str,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[
    ResponseErrorMetaSingle
    | ResponseVariableIncomesBroker
    | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423
]:
    """Obtém as informações da nota de negociação identificado nas movimentações de compra e venda de
    ativos em bolsa.
    O brokerNoteId é enviado nos movimentos de compra ou venda de ativos e deve ser passada como
    parâmetro de entrada no endpoint “Nota de Negociação”.Como conteúdo do campo brokerNoteId é esperado
    que a transmissora gere um identificar único, imutável, para cada número (natural) de nota de
    negociação.

     Obtém as informações da nota de negociação identificado nas movimentações de compra e venda de
    ativos em bolsa.
    O brokerNoteId é enviado nos movimentos de compra ou venda de ativos e deve ser passada como
    parâmetro de entrada no endpoint “Nota de Negociação”.Como conteúdo do campo brokerNoteId é esperado
    que a transmissora gere um identificar único, imutável, para cada número (natural) de nota de
    negociação.

    Args:
        broker_note_id (str):  Example: 92792126019929200000000000000000000000000.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (str):
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseErrorMetaSingle | ResponseVariableIncomesBroker | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423]
    """

    kwargs = _get_kwargs(
        broker_note_id=broker_note_id,
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
    broker_note_id: str,
    *,
    client: AuthenticatedClient,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: str,
    x_customer_user_agent: str | Unset = UNSET,
) -> (
    ResponseErrorMetaSingle
    | ResponseVariableIncomesBroker
    | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423
    | None
):
    """Obtém as informações da nota de negociação identificado nas movimentações de compra e venda de
    ativos em bolsa.
    O brokerNoteId é enviado nos movimentos de compra ou venda de ativos e deve ser passada como
    parâmetro de entrada no endpoint “Nota de Negociação”.Como conteúdo do campo brokerNoteId é esperado
    que a transmissora gere um identificar único, imutável, para cada número (natural) de nota de
    negociação.

     Obtém as informações da nota de negociação identificado nas movimentações de compra e venda de
    ativos em bolsa.
    O brokerNoteId é enviado nos movimentos de compra ou venda de ativos e deve ser passada como
    parâmetro de entrada no endpoint “Nota de Negociação”.Como conteúdo do campo brokerNoteId é esperado
    que a transmissora gere um identificar único, imutável, para cada número (natural) de nota de
    negociação.

    Args:
        broker_note_id (str):  Example: 92792126019929200000000000000000000000000.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (str):
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseErrorMetaSingle | ResponseVariableIncomesBroker | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423
    """

    return sync_detailed(
        broker_note_id=broker_note_id,
        client=client,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    ).parsed


async def asyncio_detailed(
    broker_note_id: str,
    *,
    client: AuthenticatedClient,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: str,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[
    ResponseErrorMetaSingle
    | ResponseVariableIncomesBroker
    | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423
]:
    """Obtém as informações da nota de negociação identificado nas movimentações de compra e venda de
    ativos em bolsa.
    O brokerNoteId é enviado nos movimentos de compra ou venda de ativos e deve ser passada como
    parâmetro de entrada no endpoint “Nota de Negociação”.Como conteúdo do campo brokerNoteId é esperado
    que a transmissora gere um identificar único, imutável, para cada número (natural) de nota de
    negociação.

     Obtém as informações da nota de negociação identificado nas movimentações de compra e venda de
    ativos em bolsa.
    O brokerNoteId é enviado nos movimentos de compra ou venda de ativos e deve ser passada como
    parâmetro de entrada no endpoint “Nota de Negociação”.Como conteúdo do campo brokerNoteId é esperado
    que a transmissora gere um identificar único, imutável, para cada número (natural) de nota de
    negociação.

    Args:
        broker_note_id (str):  Example: 92792126019929200000000000000000000000000.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (str):
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ResponseErrorMetaSingle | ResponseVariableIncomesBroker | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423]
    """

    kwargs = _get_kwargs(
        broker_note_id=broker_note_id,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    broker_note_id: str,
    *,
    client: AuthenticatedClient,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: str,
    x_customer_user_agent: str | Unset = UNSET,
) -> (
    ResponseErrorMetaSingle
    | ResponseVariableIncomesBroker
    | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423
    | None
):
    """Obtém as informações da nota de negociação identificado nas movimentações de compra e venda de
    ativos em bolsa.
    O brokerNoteId é enviado nos movimentos de compra ou venda de ativos e deve ser passada como
    parâmetro de entrada no endpoint “Nota de Negociação”.Como conteúdo do campo brokerNoteId é esperado
    que a transmissora gere um identificar único, imutável, para cada número (natural) de nota de
    negociação.

     Obtém as informações da nota de negociação identificado nas movimentações de compra e venda de
    ativos em bolsa.
    O brokerNoteId é enviado nos movimentos de compra ou venda de ativos e deve ser passada como
    parâmetro de entrada no endpoint “Nota de Negociação”.Como conteúdo do campo brokerNoteId é esperado
    que a transmissora gere um identificar único, imutável, para cada número (natural) de nota de
    negociação.

    Args:
        broker_note_id (str):  Example: 92792126019929200000000000000000000000000.
        authorization (str):
        x_fapi_auth_date (str | Unset):
        x_fapi_customer_ip_address (str | Unset):
        x_fapi_interaction_id (str):
        x_customer_user_agent (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ResponseErrorMetaSingle | ResponseVariableIncomesBroker | VariableIncomesGetInvestmentsInvestmentIdBrokerNotesBrokerNoteIdResponse423
    """

    return (
        await asyncio_detailed(
            broker_note_id=broker_note_id,
            client=client,
            authorization=authorization,
            x_fapi_auth_date=x_fapi_auth_date,
            x_fapi_customer_ip_address=x_fapi_customer_ip_address,
            x_fapi_interaction_id=x_fapi_interaction_id,
            x_customer_user_agent=x_customer_user_agent,
        )
    ).parsed
