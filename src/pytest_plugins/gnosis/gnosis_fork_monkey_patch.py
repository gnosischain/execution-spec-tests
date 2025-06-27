"""Fork parameter monkey patching for Gnosis customizations."""

from typing import Any, Dict, Optional, Type

from ethereum_test_forks.base_fork import BaseFork

# Import Gnosis defaults to keep values in sync
from .gnosis import (DEFAULT_GNOSIS_BLOB_BASE_FEE_UPDATE_FRACTION,
                     DEFAULT_GNOSIS_MAX_BLOBS_PER_BLOCK,
                     DEFAULT_GNOSIS_TARGET_BLOBS_PER_BLOCK)

# Store original fork methods for restoration
_original_fork_methods: Dict[Type[BaseFork], Dict[str, Any]] = {}

# Store custom parameters to apply
_custom_fork_params: Dict[str, Any] = {}


def set_custom_fork_parameters(
    blob_base_fee_update_fraction: Optional[int] = None,
    target_blobs_per_block: Optional[int] = None,
    max_blobs_per_block: Optional[int] = None,
) -> None:
    """Set custom fork parameters that will be applied to any fork.
    
    If None is provided for a parameter, the corresponding Gnosis default will be used.
    Default values:
    - blob_base_fee_update_fraction: DEFAULT_GNOSIS_BLOB_BASE_FEE_UPDATE_FRACTION ({DEFAULT_GNOSIS_BLOB_BASE_FEE_UPDATE_FRACTION})
    - target_blobs_per_block: DEFAULT_GNOSIS_TARGET_BLOBS_PER_BLOCK ({DEFAULT_GNOSIS_TARGET_BLOBS_PER_BLOCK})
    - max_blobs_per_block: DEFAULT_GNOSIS_MAX_BLOBS_PER_BLOCK ({DEFAULT_GNOSIS_MAX_BLOBS_PER_BLOCK})
    """
    global _custom_fork_params
    
    _custom_fork_params = {}
    if blob_base_fee_update_fraction is not None:
        _custom_fork_params['blob_base_fee_update_fraction'] = blob_base_fee_update_fraction
    if target_blobs_per_block is not None:
        _custom_fork_params['target_blobs_per_block'] = target_blobs_per_block
    if max_blobs_per_block is not None:
        _custom_fork_params['max_blobs_per_block'] = max_blobs_per_block


def apply_gnosis_defaults_to_all_forks() -> None:
    """Apply Gnosis default fork parameters to all blob-supporting forks.
    
    This is useful when you want to make all forks use Gnosis-like defaults
    without specifying custom values.
    """
    set_custom_fork_parameters(
        blob_base_fee_update_fraction=DEFAULT_GNOSIS_BLOB_BASE_FEE_UPDATE_FRACTION,
        target_blobs_per_block=DEFAULT_GNOSIS_TARGET_BLOBS_PER_BLOCK,
        max_blobs_per_block=DEFAULT_GNOSIS_MAX_BLOBS_PER_BLOCK,
    )
    patch_fork_parameters()


def patch_fork_parameters() -> None:
    """Monkey patch all fork classes to use custom parameters when available."""
    # Import here to avoid circular imports
    from ethereum_test_forks import get_forks
    
    if not _custom_fork_params:
        return  # No custom parameters to apply
    
    print(f"🔧 Patching fork parameters: {_custom_fork_params}")
    
    # Get all available forks
    forks = get_forks()
    
    for fork_class in forks:
        # Skip if this fork doesn't support blobs
        if not hasattr(fork_class, 'supports_blobs'):
            continue
            
        try:
            # Check if fork supports blobs at all
            if not fork_class.supports_blobs():
                continue
        except NotImplementedError:
            continue
        
        # Store original methods if not already stored
        if fork_class not in _original_fork_methods:
            _original_fork_methods[fork_class] = {}
            
            # Store original methods
            if hasattr(fork_class, 'blob_base_fee_update_fraction'):
                _original_fork_methods[fork_class]['blob_base_fee_update_fraction'] = fork_class.blob_base_fee_update_fraction
            if hasattr(fork_class, 'target_blobs_per_block'):
                _original_fork_methods[fork_class]['target_blobs_per_block'] = fork_class.target_blobs_per_block
            if hasattr(fork_class, 'max_blobs_per_block'):
                _original_fork_methods[fork_class]['max_blobs_per_block'] = fork_class.max_blobs_per_block
        
        # Patch blob_base_fee_update_fraction if specified
        if 'blob_base_fee_update_fraction' in _custom_fork_params:
            custom_value = _custom_fork_params['blob_base_fee_update_fraction']
            setattr(fork_class, 'blob_base_fee_update_fraction', 
                   classmethod(lambda cls, block_number=0, timestamp=0, value=custom_value: value))
        
        # Patch target_blobs_per_block if specified
        if 'target_blobs_per_block' in _custom_fork_params:
            custom_value = _custom_fork_params['target_blobs_per_block']
            setattr(fork_class, 'target_blobs_per_block',
                   classmethod(lambda cls, block_number=0, timestamp=0, value=custom_value: value))
        
        # Patch max_blobs_per_block if specified
        if 'max_blobs_per_block' in _custom_fork_params:
            custom_value = _custom_fork_params['max_blobs_per_block']
            setattr(fork_class, 'max_blobs_per_block',
                   classmethod(lambda cls, block_number=0, timestamp=0, value=custom_value: value))
        
        print(f"  ✓ Patched {fork_class.__name__}")


def restore_fork_parameters() -> None:
    """Restore original fork methods."""
    for fork_class, methods in _original_fork_methods.items():
        for method_name, original_method in methods.items():
            setattr(fork_class, method_name, original_method)
    
    _original_fork_methods.clear()
    _custom_fork_params.clear()
    print("🔄 Restored original fork parameters") 