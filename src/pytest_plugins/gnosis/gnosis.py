"""Gnosis chain fork configuration."""

from typing import Dict, List, Mapping, Type

import pytest

import ethereum_test_forks.helpers
# Attempt to import the target for monkeypatching
# This might require adjusting if the path is not directly importable here
# or if it causes circular dependencies, though unlikely for a plugin.
from ethereum_test_forks import Fork, London
from ethereum_test_forks.base_fork import BaseFork
from ethereum_test_forks.helpers import get_forks


class Gnosis(London, blockchain_test_network_name="gnosis"):
    """Gnosis chain fork class.
    
    Currently based on London fork, but can be adjusted as needed
    for specific Gnosis chain parameters.
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
    def pre_allocation_blockchain(cls) -> Mapping:
        """Return the pre-allocation mapping for the Gnosis chain."""
        # Gnosis chain pre-allocations would go here
        # For now, using a minimal set for testing
        return {
            "0x0000000000000000000000000000000000000000": {
                "balance": "0x0",
                "nonce": "0x0",
                "code": "0x",
                "storage": {}
            }
        }


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

    # Remove the previous monkeypatch for filler_module.pytest_collection_modifyitems
    # as it's no longer needed with this approach.

    # original_filler_collection_modifyitems = getattr(filler_module, "pytest_collection_modifyitems", None)
    # if original_filler_collection_modifyitems:
    #     def patched_filler_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    #         gnosis_registration_test_node_id = "tests/test_gnosis_plugin_registration.py::test_gnosis_fork_is_registered_via_pytest_plugin"
    #         our_test_items = []
    #         other_items = []
    #         for item in items:
    #             if item.nodeid == gnosis_registration_test_node_id:
    #                 our_test_items.append(item)
    #             else:
    #                 other_items.append(item)
    #         processed_other_items = list(other_items)
    #         original_filler_collection_modifyitems(config, processed_other_items)
    #         items.clear()
    #         items.extend(our_test_items)
    #         items.extend(processed_other_items)
    #     monkeypatch.setattr(filler_module, "pytest_collection_modifyitems", patched_filler_collection_modifyitems)
    # else:
    #     print("\nWARNING: Could not find original pytest_collection_modifyitems in filler_module to patch.\n") 