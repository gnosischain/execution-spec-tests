"""Pytest plugin for Gnosis chain support."""

import pytest
from _pytest.config import Config

from .gnosis import Gnosis
from .gnosis_block_types import (patch_environment_defaults_and_class,
                                 restore_environment_classes)


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


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config):
    """Configure Gnosis plugin on pytest startup."""
    # Register the plugin
    config.pluginmanager.register(GnosisPlugin(config), "gnosis_plugin")


@pytest.hookimpl(tryfirst=True)
def pytest_unconfigure(config: Config):
    """Clean up when pytest shuts down."""
    # Restore original environment defaults if they were patched
    if config.getoption("--gnosis"):
        restore_environment_classes()


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