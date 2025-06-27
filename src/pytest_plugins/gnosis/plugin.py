"""Pytest plugin for Gnosis chain support."""

import pytest
from _pytest.config import Config

from .gnosis import Gnosis, set_gnosis_fork_parameters
from .gnosis_block_types import (patch_environment_defaults_and_class,
                                 restore_environment_classes)
from .gnosis_fork_monkey_patch import (patch_fork_parameters,
                                       restore_fork_parameters,
                                       set_custom_fork_parameters)


class GnosisPlugin:
    """Plugin for Gnosis chain support in the test framework."""

    def __init__(self, config: pytest.Config):
        """Initialize the plugin."""
        self.config = config
        self.use_gnosis = config.getoption("--gnosis")
        
        if self.use_gnosis:
            # Collect all gnosis environment options
            gnosis_options = {
                'gas_limit': config.getoption("--gnosis-gas-limit"),
                'number': config.getoption("--gnosis-number"),
                'timestamp': config.getoption("--gnosis-timestamp"),
                'base_fee_per_gas': config.getoption("--gnosis-base-fee"),
                'difficulty': config.getoption("--gnosis-difficulty"),
                'excess_blob_gas': config.getoption("--gnosis-excess-blob-gas"),
            }
            
            # Remove None values
            gnosis_options = {k: v for k, v in gnosis_options.items() if v is not None}
            
            # Apply environment defaults patching if gnosis is enabled
            patch_environment_defaults_and_class(**gnosis_options)
        
        # Gnosis fork is now auto-registered by a session fixture in gnosis.py
        # No need to call register_gnosis_fork() here anymore.


def pytest_addoption(parser):
    """Add command-line options for Gnosis support."""
    gnosis_group = parser.getgroup("Gnosis", "Gnosis chain specific options")
    gnosis_group.addoption(
        "--gnosis",
        action="store_true",
        dest="gnosis",
        default=False,
        help="Use Gnosis chain for tests",
    )
    gnosis_group.addoption(
        "--gnosis-rpc",
        action="store",
        dest="gnosis_rpc",
        default="https://rpc.gnosis.gateway.fm",
        help="Gnosis RPC endpoint to use for tests",
    )
    gnosis_group.addoption(
        "--gnosis-gas-limit",
        action="store",
        dest="gnosis_gas_limit",
        type=int,
        default=None,
        help="Custom gas limit for Gnosis chain tests (default: 17,000,000)",
    )
    gnosis_group.addoption(
        "--gnosis-number",
        action="store",
        dest="gnosis_number",
        type=int,
        default=None,
        help="Default block number for Environment (default: 1)",
    )
    gnosis_group.addoption(
        "--gnosis-timestamp",
        action="store",
        dest="gnosis_timestamp",
        type=int,
        default=None,
        help="Default timestamp for Environment (default: 1000)",
    )
    gnosis_group.addoption(
        "--gnosis-base-fee",
        action="store",
        dest="gnosis_base_fee",
        type=int,
        default=None,
        help="Default base fee per gas for Environment (default: 7)",
    )
    gnosis_group.addoption(
        "--gnosis-difficulty",
        action="store",
        dest="gnosis_difficulty",
        type=int,
        default=None,
        help="Default difficulty for Environment (default: 0x20000)",
    )
    gnosis_group.addoption(
        "--gnosis-excess-blob-gas",
        action="store",
        dest="gnosis_excess_blob_gas",
        type=int,
        default=None,
        help="Default excess blob gas for Environment (default: 0)",
    )
    gnosis_group.addoption(
        "--gnosis-blob-base-fee-update-fraction",
        type=int,
        help="Set custom blob base fee update fraction for Gnosis fork"
    )
    gnosis_group.addoption(
        "--gnosis-target-blobs-per-block",
        type=int,
        help="Set custom target blobs per block for Gnosis fork"
    )
    gnosis_group.addoption(
        "--gnosis-max-blobs-per-block",
        type=int,
        help="Set custom max blobs per block for Gnosis fork"
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config):
    """Configure Gnosis plugin on pytest startup."""
    # Register the plugin
    config.pluginmanager.register(GnosisPlugin(config), "gnosis_plugin")
    
    # Check if Gnosis mode is enabled
    use_gnosis = config.getoption("--gnosis")
    
    # Configure fork parameters if Gnosis is enabled or any are specified
    blob_base_fee_update_fraction = config.getoption("--gnosis-blob-base-fee-update-fraction")
    target_blobs_per_block = config.getoption("--gnosis-target-blobs-per-block")
    max_blobs_per_block = config.getoption("--gnosis-max-blobs-per-block")
    
    fork_options = [blob_base_fee_update_fraction, target_blobs_per_block, max_blobs_per_block]
    
    # Apply fork parameters if:
    # 1. Any specific blob parameters are provided, OR
    # 2. Gnosis mode is enabled (use defaults)
    if any(fork_options) or use_gnosis:
        print("\n=== Gnosis Fork Configuration ===")
        
        # Import defaults for display and fallback
        from .gnosis import (DEFAULT_GNOSIS_BLOB_BASE_FEE_UPDATE_FRACTION,
                             DEFAULT_GNOSIS_MAX_BLOBS_PER_BLOCK,
                             DEFAULT_GNOSIS_TARGET_BLOBS_PER_BLOCK)

        # Use provided values or fall back to Gnosis defaults if in Gnosis mode
        final_blob_base_fee_update_fraction = blob_base_fee_update_fraction
        final_target_blobs_per_block = target_blobs_per_block
        final_max_blobs_per_block = max_blobs_per_block
        
        if use_gnosis:
            # Apply Gnosis defaults for any unspecified parameters
            if final_blob_base_fee_update_fraction is None:
                final_blob_base_fee_update_fraction = DEFAULT_GNOSIS_BLOB_BASE_FEE_UPDATE_FRACTION
            if final_target_blobs_per_block is None:
                final_target_blobs_per_block = DEFAULT_GNOSIS_TARGET_BLOBS_PER_BLOCK
            if final_max_blobs_per_block is None:
                final_max_blobs_per_block = DEFAULT_GNOSIS_MAX_BLOBS_PER_BLOCK
        
        # Set custom parameters for Gnosis fork (legacy)
        fork_params = {}
        if final_blob_base_fee_update_fraction is not None:
            fork_params['blob_base_fee_update_fraction'] = final_blob_base_fee_update_fraction
        if final_target_blobs_per_block is not None:
            fork_params['target_blobs_per_block'] = final_target_blobs_per_block
        if final_max_blobs_per_block is not None:
            fork_params['max_blobs_per_block'] = final_max_blobs_per_block
        
        set_gnosis_fork_parameters(**fork_params)
        
        # Also set custom parameters for ALL forks (new approach)
        set_custom_fork_parameters(
            blob_base_fee_update_fraction=final_blob_base_fee_update_fraction,
            target_blobs_per_block=final_target_blobs_per_block,
            max_blobs_per_block=final_max_blobs_per_block
        )
        
        # Apply the patches to all fork classes
        patch_fork_parameters()
        
        if use_gnosis:
            print("✓ Gnosis defaults applied to ALL forks")
        else:
            print("✓ Custom fork parameters configured for ALL forks")
        
        # Display configured fork parameters
        if final_blob_base_fee_update_fraction is not None:
            print(f"  - Blob base fee update fraction: {final_blob_base_fee_update_fraction}")
        if final_target_blobs_per_block is not None:
            print(f"  - Target blobs per block: {final_target_blobs_per_block}")
        if final_max_blobs_per_block is not None:
            print(f"  - Max blobs per block: {final_max_blobs_per_block}")
        
        print("=== End Gnosis Fork Configuration ===\n")


@pytest.hookimpl(tryfirst=True)
def pytest_unconfigure(config: Config):
    """Clean up when pytest shuts down."""
    # Restore original environment defaults if they were patched
    if config.getoption("--gnosis"):
        restore_environment_classes()
    
    # Restore original fork parameters
    restore_fork_parameters()


@pytest.fixture
def gnosis_network(request):
    """Provide Gnosis network configuration as a fixture."""
    return {
        "name": "gnosis",
        "fork": Gnosis,
        "chain_id": 100,
        "rpc_url": request.config.getoption("--gnosis-rpc"),
    }


@pytest.fixture
def is_gnosis_network(request):
    """Check if tests are running against Gnosis network."""
    return request.config.getoption("--gnosis")


 