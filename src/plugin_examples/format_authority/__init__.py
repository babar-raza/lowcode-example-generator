"""FormatContract authority — single source of truth for format decisions."""

from plugin_examples.format_authority.contracts import FormatContract
from plugin_examples.format_authority.store import (
    MissingFormatContractError,
    get_all_contracts,
    get_contract,
    load_contracts_from_json,
)

__all__ = [
    "FormatContract",
    "get_contract",
    "get_all_contracts",
    "load_contracts_from_json",
    "MissingFormatContractError",
]
