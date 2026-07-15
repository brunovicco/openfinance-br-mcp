"""Vendored, OpenAPI-generated typed HTTP clients for Open Finance Brasil.

Each subpackage here is generated verbatim by ``openapi-python-client``
from the official spec at one API family's current stable version
(github.com/OpenBanking-Brasil/openapi/swagger-apis/<family>/<version>.yml),
verified directly against a local clone of that repository as part of
``IMPLEMENTATION_PLAN.md`` P1.1 - the versions below are the real,
confirmed stable releases, not the ones originally guessed in the plan
(e.g. accounts is 2.4.2, not 2.5.0; credit-cards-accounts is 2.3.1, not
2.4.0; payments is 4.0.0, 5.0.0 does not exist).

This directory is generated/vendored third-party code: it is excluded
from ``ruff``/``mypy`` in ``pyproject.toml`` and should not be
hand-edited - regenerate it instead if a family's spec version changes.
Every internal import across all 8 packages was rewritten from
``openapi-python-client``'s default dot-relative style (``from ...client
import Client``) to fully-qualified absolute imports rooted at
``clients`` (``from clients.accounts_v2_4_2.client import Client``),
so every file's imports are unambiguous on their own regardless of how
or from where it's imported.

Known limitation (see each family's ``api/`` package): ``openapi-
python-client`` cannot generate typed methods for any operation whose
request/response body content-type is ``application/jwt`` (a signed
JWS) - it silently skips them. This affects every write endpoint of
the Payments API (``POST /consents``, ``POST /pix/payments``, the
cancel ``PATCH``), which remain hand-written with manual JWS signing
in ``adapters/default_adapter.py``/``auth/payment_jws.py``/
``auth/payment_consent.py`` instead. Only ``payments_v4_0_0``'s two
GET/query operations were actually generated.

Each family exposes a ``Client``/``AuthenticatedClient`` pair (this
module re-exports them below under per-family aliases, since the
generated classes all share the same bare names) supporting
``set_async_httpx_client()`` - the intended integration point for
injecting this project's own mTLS-configured ``httpx.AsyncClient``
into a generated client without losing certificate configuration, once
these clients are wired into the adapters (tracked separately, not yet
done as of this vendoring).

Example:
    >>> from clients import AccountsClient
    >>> from clients.accounts_v2_4_2.api.accounts import accounts_get_accounts
    >>> client = AccountsClient(base_url="https://api.bank.com.br/open-banking")
    >>> client.set_async_httpx_client(my_mtls_configured_async_client)
    >>> accounts = await accounts_get_accounts.asyncio(client=client)
"""

from clients.accounts_v2_4_2 import AuthenticatedClient as AccountsAuthenticatedClient
from clients.accounts_v2_4_2 import Client as AccountsClient
from clients.bank_fixed_incomes_v1_1_0 import (
    AuthenticatedClient as BankFixedIncomesAuthenticatedClient,
)
from clients.bank_fixed_incomes_v1_1_0 import Client as BankFixedIncomesClient
from clients.consents_v3_3_1 import AuthenticatedClient as ConsentsAuthenticatedClient
from clients.consents_v3_3_1 import Client as ConsentsClient
from clients.credit_cards_v2_3_1 import (
    AuthenticatedClient as CreditCardsAuthenticatedClient,
)
from clients.credit_cards_v2_3_1 import Client as CreditCardsClient
from clients.funds_v1_1_0 import AuthenticatedClient as FundsAuthenticatedClient
from clients.funds_v1_1_0 import Client as FundsClient
from clients.payments_v4_0_0 import AuthenticatedClient as PaymentsAuthenticatedClient
from clients.payments_v4_0_0 import Client as PaymentsClient
from clients.treasure_titles_v1_1_0 import (
    AuthenticatedClient as TreasureTitlesAuthenticatedClient,
)
from clients.treasure_titles_v1_1_0 import Client as TreasureTitlesClient
from clients.variable_incomes_v1_3_0 import (
    AuthenticatedClient as VariableIncomesAuthenticatedClient,
)
from clients.variable_incomes_v1_3_0 import Client as VariableIncomesClient

__all__ = (
    "AccountsAuthenticatedClient",
    "AccountsClient",
    "BankFixedIncomesAuthenticatedClient",
    "BankFixedIncomesClient",
    "ConsentsAuthenticatedClient",
    "ConsentsClient",
    "CreditCardsAuthenticatedClient",
    "CreditCardsClient",
    "FundsAuthenticatedClient",
    "FundsClient",
    "PaymentsAuthenticatedClient",
    "PaymentsClient",
    "TreasureTitlesAuthenticatedClient",
    "TreasureTitlesClient",
    "VariableIncomesAuthenticatedClient",
    "VariableIncomesClient",
)
