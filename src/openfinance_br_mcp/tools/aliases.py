"""Shared type aliases for MCP tool signatures.

Centralizing ``BankId`` here means FastMCP auto-generates the same
enum constraint in every tool's JSON Schema from a single source of
truth. Adding a new bank still requires registering its adapter in
``context.py`` (see README "Adding a new bank") - this alias must be
updated in the same change.
"""

from typing import Annotated, Literal

from pydantic import Field

BankId = Literal[
    "nubank",
    "sicoob",
    "caixa",
    "banco_do_brasil",
    "bradesco",
    "itau",
    "santander",
    "xp",
    "picpay",
    "btg",
]

ConsentScope = Literal[
    "accounts",
    "balances",
    "transactions",
    "overdraft_limits",
    "credit_card_accounts",
    "credit_card_limits",
    "credit_card_bills",
    "credit_card_transactions",
    "bank_fixed_incomes",
    "funds",
    "variable_incomes",
    "treasure_titles",
]
"""Data-sharing scopes accepted by the consent flow."""

ConsentScopes = Annotated[list[ConsentScope], Field(min_length=1)]
"""Non-empty, schema-constrained list of data-sharing scopes."""
