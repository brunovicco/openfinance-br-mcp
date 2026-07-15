"""MCP resources and prompts exposed alongside the server's tools.

Tools remain the primary integration surface, but these primitives make
stable server context discoverable without a tool call and provide a
user-controlled workflow template for a common financial analysis task.
"""

import json
from typing import get_args

from mcp.server.fastmcp import FastMCP

from openfinance_br_mcp.config import settings
from openfinance_br_mcp.tools.aliases import BankId

_BANK_NAMES = {
    "nubank": "Nubank",
    "sicoob": "Sicoob",
    "caixa": "Caixa Economica Federal",
    "banco_do_brasil": "Banco do Brasil",
    "bradesco": "Bradesco",
    "itau": "Itau Unibanco",
    "santander": "Santander",
    "xp": "XP",
    "picpay": "PicPay",
    "btg": "BTG Pactual",
}


def supported_banks() -> str:
    """Return the configured banks and discovery mode."""
    payload = {
        "service": settings.server_name,
        "version": settings.server_version,
        "environment": settings.environment,
        "banks": [
            {
                "id": bank_id,
                "name": _BANK_NAMES[bank_id],
                "configured": True,
                "availability": (
                    "available"
                    if settings.environment == "mock"
                    else "directory-dependent"
                ),
                "mode": "mock" if settings.environment == "mock" else "directory",
            }
            for bank_id in get_args(BankId)
        ],
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True)


def analyze_monthly_spending(
    bank: BankId,
    date_from: str,
    date_to: str,
    category: str = "",
) -> str:
    """Create a guided workflow for analysing transactions in a date range."""
    category_instruction = (
        f" Focus the analysis on the '{category}' category." if category else ""
    )
    return (
        f"Use list_transactions for bank='{bank}', date_from='{date_from}', "
        f"date_to='{date_to}', and categorize=true.{category_instruction} "
        "Summarize total spending, income, the largest transactions, category "
        "breakdown, recurring charges, and unusual changes. Clearly distinguish "
        "facts returned by the tool from interpretations, and format monetary "
        "values in BRL."
    )


def register_mcp_primitives(mcp: FastMCP) -> None:
    """Register the project's resource and prompt primitives."""
    mcp.resource(
        "openfinance://banks/",
        name="supported_banks",
        title="Supported Open Finance Banks",
        description=(
            "Banks known by the server and how availability is determined in "
            "the current environment."
        ),
        mime_type="application/json",
    )(supported_banks)
    mcp.prompt(
        name="analyze_monthly_spending",
        title="Analyze Monthly Spending",
        description=(
            "Guide the model through a categorized transaction analysis for a "
            "bank and date range."
        ),
    )(analyze_monthly_spending)
