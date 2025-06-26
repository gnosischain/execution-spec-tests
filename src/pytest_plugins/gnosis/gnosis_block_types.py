"""Modified block types for Gnosis chain support."""

from dataclasses import dataclass
from typing import Any, Optional

# Gnosis chain specific defaults
GNOSIS_DEFAULT_BASE_FEE = 7
GNOSIS_CURRENT_BLOCK_GAS_LIMIT = 17_000_000  # Gnosis chain has lower gas limit than mainnet
GNOSIS_DEFAULT_BLOCK_GAS_LIMIT = GNOSIS_CURRENT_BLOCK_GAS_LIMIT


@dataclass
class GnosisEnvironmentDefaults:
    """Gnosis-specific environment defaults."""

    # Gnosis chain uses a lower gas limit than mainnet
    # Other libraries (pytest plugins) may override this value by modifying the
    # `GnosisEnvironmentDefaults.gas_limit` class attribute.
    gas_limit: int = GNOSIS_DEFAULT_BLOCK_GAS_LIMIT


# Store original defaults globally
_original_defaults: Optional[Any] = None


def patch_environment_defaults(gas_limit: Optional[int] = None) -> None:
    """
    Monkey patch the original EnvironmentDefaults to use Gnosis values.
    
    Args:
        gas_limit: Optional custom gas limit to use. If None, uses GNOSIS_DEFAULT_BLOCK_GAS_LIMIT
    """
    from ethereum_test_types import block_types
    
    global _original_defaults
    
    # Store the original for potential restoration
    if _original_defaults is None:
        _original_defaults = block_types.EnvironmentDefaults
    
    # Set the gas limit
    target_gas_limit = gas_limit if gas_limit is not None else GNOSIS_DEFAULT_BLOCK_GAS_LIMIT
    
    # Create new defaults class with custom gas limit
    @dataclass
    class PatchedEnvironmentDefaults:
        """Patched environment defaults for Gnosis chain."""
        gas_limit: int = target_gas_limit
    
    # Replace the original EnvironmentDefaults using setattr
    setattr(block_types, 'EnvironmentDefaults', PatchedEnvironmentDefaults)
    
    print(f"INFO: Patched EnvironmentDefaults.gas_limit to {target_gas_limit:,} ({hex(target_gas_limit)})")


def restore_environment_defaults() -> None:
    """Restore the original EnvironmentDefaults."""
    global _original_defaults
    
    if _original_defaults is not None:
        from ethereum_test_types import block_types
        setattr(block_types, 'EnvironmentDefaults', _original_defaults)
        print("INFO: Restored original EnvironmentDefaults") 