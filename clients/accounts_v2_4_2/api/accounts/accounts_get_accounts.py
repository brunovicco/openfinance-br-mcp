"""Accounts API - accounts operation module: Obtém a lista de contas consentidas pelo cliente."""

from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from clients.accounts_v2_4_2.client import AuthenticatedClient, Client
from clients.accounts_v2_4_2.models.enum_account_type import EnumAccountType
from clients.accounts_v2_4_2.models.response_account_list import ResponseAccountList
from clients.accounts_v2_4_2.models.response_error import ResponseError
from clients.accounts_v2_4_2.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    account_type: EnumAccountType | Unset = UNSET,
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

    json_account_type: str | Unset = UNSET
    if not isinstance(account_type, Unset):
        json_account_type = account_type.value

    params["accountType"] = json_account_type

    params["pagination-key"] = pagination_key

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/accounts",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ResponseAccountList | ResponseError:
    if response.status_code == 200:
        response_200 = ResponseAccountList.from_dict(response.json())

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
) -> Response[ResponseAccountList | ResponseError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    account_type: EnumAccountType | Unset = UNSET,
    pagination_key: str | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[ResponseAccountList | ResponseError]:
    """Obtém a lista de contas consentidas pelo cliente.

     Método para obter a lista de contas depósito à vista, poupança e pagamento pré-pagas mantidas pelo
    cliente na instituição transmissora e para as quais ele tenha fornecido consentimento.

    Args:
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        account_type (EnumAccountType | Unset): Tipos de contas. Modalidades tradicionais
            previstas pela Resolução 4.753, não contemplando contas vinculadas, conta de domiciliados
            no exterior, contas em moedas estrangeiras e conta correspondente moeda eletrônica. Vide
            Enum
            Conta de depósito à vista ou Conta corrente - é o tipo mais comum. Nela, o dinheiro fica à
            sua disposição para ser sacado a qualquer momento. Essa conta não gera rendimentos para o
            depositante
            Conta poupança - foi criada para estimular as pessoas a pouparem. O dinheiro que ficar na
            conta por trinta dias passa a gerar rendimentos, com isenção de imposto de renda para quem
            declara. Ou seja, o dinheiro “cresce” (rende) enquanto ficar guardado na conta. Cada
            depósito terá rendimentos de mês em mês, sempre no dia do mês em que o dinheiro tiver sido
            depositado
            Conta de pagamento pré-paga: segundo CIRCULAR Nº 3.680, BCB de  2013, é a 'destinada à
            execução de transações de pagamento em moeda eletrônica realizadas com base em fundos
            denominados em reais previamente aportados'
             Example: CONTA_DEPOSITO_A_VISTA.
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
        Response[ResponseAccountList | ResponseError]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        account_type=account_type,
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
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    account_type: EnumAccountType | Unset = UNSET,
    pagination_key: str | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> ResponseAccountList | ResponseError | None:
    """Obtém a lista de contas consentidas pelo cliente.

     Método para obter a lista de contas depósito à vista, poupança e pagamento pré-pagas mantidas pelo
    cliente na instituição transmissora e para as quais ele tenha fornecido consentimento.

    Args:
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        account_type (EnumAccountType | Unset): Tipos de contas. Modalidades tradicionais
            previstas pela Resolução 4.753, não contemplando contas vinculadas, conta de domiciliados
            no exterior, contas em moedas estrangeiras e conta correspondente moeda eletrônica. Vide
            Enum
            Conta de depósito à vista ou Conta corrente - é o tipo mais comum. Nela, o dinheiro fica à
            sua disposição para ser sacado a qualquer momento. Essa conta não gera rendimentos para o
            depositante
            Conta poupança - foi criada para estimular as pessoas a pouparem. O dinheiro que ficar na
            conta por trinta dias passa a gerar rendimentos, com isenção de imposto de renda para quem
            declara. Ou seja, o dinheiro “cresce” (rende) enquanto ficar guardado na conta. Cada
            depósito terá rendimentos de mês em mês, sempre no dia do mês em que o dinheiro tiver sido
            depositado
            Conta de pagamento pré-paga: segundo CIRCULAR Nº 3.680, BCB de  2013, é a 'destinada à
            execução de transações de pagamento em moeda eletrônica realizadas com base em fundos
            denominados em reais previamente aportados'
             Example: CONTA_DEPOSITO_A_VISTA.
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
        ResponseAccountList | ResponseError
    """

    return sync_detailed(
        client=client,
        page=page,
        page_size=page_size,
        account_type=account_type,
        pagination_key=pagination_key,
        authorization=authorization,
        x_fapi_auth_date=x_fapi_auth_date,
        x_fapi_customer_ip_address=x_fapi_customer_ip_address,
        x_fapi_interaction_id=x_fapi_interaction_id,
        x_customer_user_agent=x_customer_user_agent,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    account_type: EnumAccountType | Unset = UNSET,
    pagination_key: str | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> Response[ResponseAccountList | ResponseError]:
    """Obtém a lista de contas consentidas pelo cliente.

     Método para obter a lista de contas depósito à vista, poupança e pagamento pré-pagas mantidas pelo
    cliente na instituição transmissora e para as quais ele tenha fornecido consentimento.

    Args:
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        account_type (EnumAccountType | Unset): Tipos de contas. Modalidades tradicionais
            previstas pela Resolução 4.753, não contemplando contas vinculadas, conta de domiciliados
            no exterior, contas em moedas estrangeiras e conta correspondente moeda eletrônica. Vide
            Enum
            Conta de depósito à vista ou Conta corrente - é o tipo mais comum. Nela, o dinheiro fica à
            sua disposição para ser sacado a qualquer momento. Essa conta não gera rendimentos para o
            depositante
            Conta poupança - foi criada para estimular as pessoas a pouparem. O dinheiro que ficar na
            conta por trinta dias passa a gerar rendimentos, com isenção de imposto de renda para quem
            declara. Ou seja, o dinheiro “cresce” (rende) enquanto ficar guardado na conta. Cada
            depósito terá rendimentos de mês em mês, sempre no dia do mês em que o dinheiro tiver sido
            depositado
            Conta de pagamento pré-paga: segundo CIRCULAR Nº 3.680, BCB de  2013, é a 'destinada à
            execução de transações de pagamento em moeda eletrônica realizadas com base em fundos
            denominados em reais previamente aportados'
             Example: CONTA_DEPOSITO_A_VISTA.
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
        Response[ResponseAccountList | ResponseError]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        account_type=account_type,
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
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | Unset = 25,
    account_type: EnumAccountType | Unset = UNSET,
    pagination_key: str | Unset = UNSET,
    authorization: str,
    x_fapi_auth_date: str | Unset = UNSET,
    x_fapi_customer_ip_address: str | Unset = UNSET,
    x_fapi_interaction_id: UUID,
    x_customer_user_agent: str | Unset = UNSET,
) -> ResponseAccountList | ResponseError | None:
    """Obtém a lista de contas consentidas pelo cliente.

     Método para obter a lista de contas depósito à vista, poupança e pagamento pré-pagas mantidas pelo
    cliente na instituição transmissora e para as quais ele tenha fornecido consentimento.

    Args:
        page (int | Unset):  Default: 1.
        page_size (int | Unset):  Default: 25.
        account_type (EnumAccountType | Unset): Tipos de contas. Modalidades tradicionais
            previstas pela Resolução 4.753, não contemplando contas vinculadas, conta de domiciliados
            no exterior, contas em moedas estrangeiras e conta correspondente moeda eletrônica. Vide
            Enum
            Conta de depósito à vista ou Conta corrente - é o tipo mais comum. Nela, o dinheiro fica à
            sua disposição para ser sacado a qualquer momento. Essa conta não gera rendimentos para o
            depositante
            Conta poupança - foi criada para estimular as pessoas a pouparem. O dinheiro que ficar na
            conta por trinta dias passa a gerar rendimentos, com isenção de imposto de renda para quem
            declara. Ou seja, o dinheiro “cresce” (rende) enquanto ficar guardado na conta. Cada
            depósito terá rendimentos de mês em mês, sempre no dia do mês em que o dinheiro tiver sido
            depositado
            Conta de pagamento pré-paga: segundo CIRCULAR Nº 3.680, BCB de  2013, é a 'destinada à
            execução de transações de pagamento em moeda eletrônica realizadas com base em fundos
            denominados em reais previamente aportados'
             Example: CONTA_DEPOSITO_A_VISTA.
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
        ResponseAccountList | ResponseError
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            page_size=page_size,
            account_type=account_type,
            pagination_key=pagination_key,
            authorization=authorization,
            x_fapi_auth_date=x_fapi_auth_date,
            x_fapi_customer_ip_address=x_fapi_customer_ip_address,
            x_fapi_interaction_id=x_fapi_interaction_id,
            x_customer_user_agent=x_customer_user_agent,
        )
    ).parsed
