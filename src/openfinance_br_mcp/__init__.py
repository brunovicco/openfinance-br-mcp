"""Openfinance-br-mcp - MCP Server for Brazilian Open Finance.

Main package of the MCP server that abstracts the Banco Central do
Brasil (Open Finance) APIs, exposing tools for Claude.

Supported phases:
    - Fase 2: Account, card, transaction, and balance data.
    - Fase 3: PIX payment initiation.
    - Fase 4: Fixed-income investments.

Participating banks included:
    - Nubank (ISPB: 18236120)
    - Sicoob (ISPB: 04891850)
    - Caixa Econômica Federal (ISPB: 00360305)
    - Banco do Brasil (ISPB: 00000000)
    - Bradesco (ISPB: 60746948)
    - Itaú Unibanco (ISPB: 60701190)
    - Santander (ISPB: 90400888)
    - XP (ISPB: 33264668)
    - PicPay (ISPB: 22896431)
    - BTG Pactual (ISPB: 30306294)
"""

__version__ = "0.1.0"
__author__ = "openfinance-br-mcp contributors"
