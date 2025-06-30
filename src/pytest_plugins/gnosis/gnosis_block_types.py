"""Modified block types for Gnosis chain support."""

from dataclasses import dataclass
from typing import Any, Optional

# Gnosis chain specific defaults
GNOSIS_DEFAULT_BASE_FEE = 7
GNOSIS_CURRENT_BLOCK_GAS_LIMIT = 262144  # Gnosis chain has lower gas limit than mainnet
GNOSIS_DEFAULT_BLOCK_GAS_LIMIT = GNOSIS_CURRENT_BLOCK_GAS_LIMIT



@dataclass
class GnosisEnvironmentDefaults:
    """Comprehensive Gnosis-specific environment defaults."""

    # Gas and block limits
    gas_limit: int = GNOSIS_DEFAULT_BLOCK_GAS_LIMIT
    
    # Block identifiers  
    number: int = 1
    timestamp: int = 1_000
    
    # Fee mechanism
    base_fee_per_gas: int = GNOSIS_DEFAULT_BASE_FEE
    
    # Consensus
    difficulty: int = 0x20000
    prev_randao: Optional[int] = None
    
    # Blob gas (EIP-4844)
    excess_blob_gas: int = 0
    blob_gas_used: int = 0
    
    # Other defaults
    fee_recipient: str = "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba"


# Store original classes globally
_original_defaults: Optional[Any] = None
_original_environment_class: Optional[Any] = None


def patch_environment_defaults_and_class(
    gas_limit: Optional[int] = None,
    number: Optional[int] = None,
    timestamp: Optional[int] = None,
    base_fee_per_gas: Optional[int] = None,
    **kwargs: Any
) -> None:
    """
    Monkey patch EnvironmentDefaults and modify the Environment constructor defaults.
    
    Args:
        gas_limit: Custom gas limit
        number: Custom block number default
        timestamp: Custom timestamp default  
        base_fee_per_gas: Custom base fee default
        **kwargs: Other environment defaults
    """
    from ethereum_test_types import block_types
    
    global _original_defaults, _original_environment_class
    
    # Store originals for potential restoration
    if _original_defaults is None:
        _original_defaults = block_types.EnvironmentDefaults
    if _original_environment_class is None:
        _original_environment_class = block_types.Environment
    
    # Create custom defaults
    custom_defaults = GnosisEnvironmentDefaults()
    
    # Apply custom values
    if gas_limit is not None:
        custom_defaults.gas_limit = gas_limit
    if number is not None:
        custom_defaults.number = number
    if timestamp is not None:
        custom_defaults.timestamp = timestamp
    if base_fee_per_gas is not None:
        custom_defaults.base_fee_per_gas = base_fee_per_gas
    
    # Apply any additional kwargs
    for key, value in kwargs.items():
        if hasattr(custom_defaults, key):
            setattr(custom_defaults, key, value)
    
    # Create patched EnvironmentDefaults
    @dataclass
    class PatchedEnvironmentDefaults:
        """Patched environment defaults for Gnosis chain."""
        gas_limit: int = custom_defaults.gas_limit
    
    # Replace EnvironmentDefaults
    setattr(block_types, 'EnvironmentDefaults', PatchedEnvironmentDefaults)
    
    # Monkey patch the Environment class's __init__ method to use our custom defaults
    original_init = _original_environment_class.__init__
    
    def patched_init(self, **kwargs_init):
        # Set our custom defaults if not provided in kwargs
        if 'number' not in kwargs_init:
            kwargs_init['number'] = custom_defaults.number
        if 'timestamp' not in kwargs_init:
            kwargs_init['timestamp'] = custom_defaults.timestamp
        if 'base_fee_per_gas' not in kwargs_init:
            kwargs_init['base_fee_per_gas'] = custom_defaults.base_fee_per_gas
        if 'difficulty' not in kwargs_init:
            kwargs_init['difficulty'] = custom_defaults.difficulty
        if 'prev_randao' not in kwargs_init and custom_defaults.prev_randao is not None:
            kwargs_init['prev_randao'] = custom_defaults.prev_randao
        if 'excess_blob_gas' not in kwargs_init:
            kwargs_init['excess_blob_gas'] = custom_defaults.excess_blob_gas
        if 'blob_gas_used' not in kwargs_init:
            kwargs_init['blob_gas_used'] = custom_defaults.blob_gas_used
        if 'fee_recipient' not in kwargs_init:
            from ethereum_test_base_types import Address
            kwargs_init['fee_recipient'] = Address(custom_defaults.fee_recipient)
        
        # Call the original init
        original_init(self, **kwargs_init)
    
    # Replace the Environment class's __init__ method
    setattr(block_types.Environment, '__init__', patched_init)
    
    print(f"INFO: Patched Environment class with custom defaults:")
    print(f"  - gas_limit: {custom_defaults.gas_limit:,} ({hex(custom_defaults.gas_limit)})")
    print(f"  - number: {custom_defaults.number}")
    print(f"  - timestamp: {custom_defaults.timestamp}")
    print(f"  - base_fee_per_gas: {custom_defaults.base_fee_per_gas}")
    print(f"  - difficulty: {hex(custom_defaults.difficulty)}")
    print(f"  - excess_blob_gas: {custom_defaults.excess_blob_gas}")


def patch_environment_defaults(gas_limit: Optional[int] = None) -> None:
    """
    Backward compatibility function - delegates to patch_environment_defaults_and_class.
    """
    patch_environment_defaults_and_class(gas_limit=gas_limit)


def restore_environment_classes() -> None:
    """Restore the original Environment classes."""
    global _original_defaults, _original_environment_class
    
    if _original_defaults is not None and _original_environment_class is not None:
        from ethereum_test_types import block_types
        setattr(block_types, 'EnvironmentDefaults', _original_defaults)
        setattr(block_types.Environment, '__init__', _original_environment_class.__init__)
        print("INFO: Restored original Environment classes")


def restore_environment_defaults() -> None:
    """Backward compatibility function - delegates to restore_environment_classes."""
    restore_environment_classes() 