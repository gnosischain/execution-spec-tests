"""Pytest plugin for Gnosis chain support."""

import pytest
from _pytest.config import Config

from .gnosis import Gnosis, register_gnosis_fork


class GnosisPlugin:
    """Plugin for Gnosis chain support in the test framework."""

    def __init__(self, config: pytest.Config):
        """Initialize the plugin."""
        self.config = config
        self.use_gnosis = config.getoption("--gnosis")
        
        # Register Gnosis fork
        if self.use_gnosis:
            register_gnosis_fork()


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


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config):
    """Configure Gnosis plugin on pytest startup."""
    # Register the plugin
    config.pluginmanager.register(GnosisPlugin(config), "gnosis_plugin")


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