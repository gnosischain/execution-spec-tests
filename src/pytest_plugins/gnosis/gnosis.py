"""Gnosis chain fork configuration."""

from typing import Dict, List, Mapping, Type

import pytest

import ethereum_test_forks.helpers
# Attempt to import the target for monkeypatching
# This might require adjusting if the path is not directly importable here
# or if it causes circular dependencies, though unlikely for a plugin.
from ethereum_test_forks import Cancun, Fork
from ethereum_test_forks.base_fork import BaseFork
from ethereum_test_forks.helpers import get_forks

# Default Gnosis chain parameters
DEFAULT_GNOSIS_BLOB_BASE_FEE_UPDATE_FRACTION = 2504285  # Custom value for Gnosis (between Cancun 3.3M and Prague 5M)
DEFAULT_GNOSIS_TARGET_BLOBS_PER_BLOCK = 1  # Custom value for Gnosis (between Cancun 3 and Prague 6)
DEFAULT_GNOSIS_MAX_BLOBS_PER_BLOCK = 2     # Custom value for Gnosis (between Cancun 6 and Prague 9)

# Global variables to store customized values (set by plugin)
_gnosis_blob_base_fee_update_fraction = DEFAULT_GNOSIS_BLOB_BASE_FEE_UPDATE_FRACTION
_gnosis_target_blobs_per_block = DEFAULT_GNOSIS_TARGET_BLOBS_PER_BLOCK
_gnosis_max_blobs_per_block = DEFAULT_GNOSIS_MAX_BLOBS_PER_BLOCK


def set_gnosis_fork_parameters(
    blob_base_fee_update_fraction: int = DEFAULT_GNOSIS_BLOB_BASE_FEE_UPDATE_FRACTION,
    target_blobs_per_block: int = DEFAULT_GNOSIS_TARGET_BLOBS_PER_BLOCK,
    max_blobs_per_block: int = DEFAULT_GNOSIS_MAX_BLOBS_PER_BLOCK,
):
    """Set global Gnosis fork parameters."""
    global _gnosis_blob_base_fee_update_fraction, _gnosis_target_blobs_per_block, _gnosis_max_blobs_per_block
    _gnosis_blob_base_fee_update_fraction = blob_base_fee_update_fraction
    _gnosis_target_blobs_per_block = target_blobs_per_block
    _gnosis_max_blobs_per_block = max_blobs_per_block


class Gnosis(Cancun, blockchain_test_network_name="gnosis"):
    """Gnosis chain fork class.
    
    Currently based on Cancun fork with Gnosis-specific parameters.
    Supports blobs with custom configuration.
    """
    
    @classmethod
    def name(cls) -> str:
        """Return the name of the fork."""
        return "Gnosis"
    
    @classmethod
    def blockchain_test_network_name(cls) -> str:
        """Return the network name for blockchain tests."""
        if cls._blockchain_test_network_name is not None:
            return cls._blockchain_test_network_name
        return "gnosis"
    
    @classmethod
    def is_deployed(cls) -> bool:
        """Indicate that this fork is deployed (not in development)."""
        return True
    
    @classmethod
    def blob_base_fee_update_fraction(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the blob base fee update fraction for Gnosis."""
        return _gnosis_blob_base_fee_update_fraction
    
    @classmethod
    def target_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the target blobs per block for Gnosis."""
        return _gnosis_target_blobs_per_block
    
    @classmethod
    def max_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the max blobs per block for Gnosis."""
        return _gnosis_max_blobs_per_block
    
    @classmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """Return the pre-allocation mapping for the Gnosis chain."""
        # Gnosis chain pre-allocations would go here
        # For now, using a minimal set for testing plus parent allocations
        gnosis_allocation = {
            "0x0000000000000000000000000000000000000000": {
                "balance": "0x3",
                "nonce": "0x0",
                "code": "0x",
                "storage": {}
            }
        }
        # Include parent allocations from Cancun
        parent_allocation = dict(super(Gnosis, cls).pre_allocation_blockchain())
        return gnosis_allocation | parent_allocation


@pytest.fixture(scope="session", autouse=True)
def gnosis_fork_registrar(monkeypatch):
    """
    Ensures the Gnosis fork is registered for the test session.
    """
    original_get_forks = ethereum_test_forks.helpers.get_forks

    def patched_get_forks() -> List[Type[BaseFork]]:
        forks = original_get_forks()
        # Check if Gnosis fork class itself is in the list, not just by name
        if not any(fork is Gnosis for fork in forks):
            forks.append(Gnosis)
        return forks

    monkeypatch.setattr(ethereum_test_forks.helpers, "get_forks", patched_get_forks)

    # Define the check logic locally to avoid circular import
    def _perform_gnosis_fork_registration_check():
        """
        Checks if the Gnosis fork is present in the list of available forks.
        This logic was moved from tests.test_gnosis_plugin_registration.
        """
        available_forks = get_forks() # This will call the patched_get_forks
        
        print("\nAvailable forks during Gnosis plugin fixture setup:")
        for fork_item in available_forks:
            print(f"- Fork Name: {fork_item.__name__}, Module: {fork_item.__module__}")
            
        assert Gnosis in available_forks, \
            "The Gnosis fork was not found in the list of available forks. " \
            "The monkeypatch in gnosis_fork_registrar might not be working correctly."

    # Call our local check function directly to verify the monkeypatch
    try:
        _perform_gnosis_fork_registration_check()
        print("\nINFO: Gnosis fork registration check PASSED (called from gnosis_fork_registrar fixture).\n")
    except AssertionError as e:
        print(f"\nERROR: Gnosis fork registration check FAILED (called from gnosis_fork_registrar fixture): {e}\n")
        # Optionally, re-raise to make the session fail if this check is critical
        raise # Re-raising to make sure a failure here stops the test session

