"""Gnosis chain fork configuration."""

from typing import Dict, List, Mapping, Type

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


def register_gnosis_fork() -> Dict[str, Type[BaseFork]]:
    """Register the Gnosis fork.
    
    This function directly adds the Gnosis fork to the list of forks
    returned by the get_forks() function.
    """
    # Get the current list of forks
    forks = get_forks()
    
    # Check if Gnosis is already in the list
    if not any(str(fork) == 'Gnosis' for fork in forks):
        # If not, append it to the list
        forks.append(Gnosis)
    
    # Set up monkey patching to ensure Gnosis is always available
    import ethereum_test_forks.helpers
    
    # Get the original get_forks function
    original_get_forks = ethereum_test_forks.helpers.get_forks
    
    # Define a wrapper function that ensures Gnosis is in the list
    def patched_get_forks() -> List[Type[BaseFork]]:
        forks = original_get_forks()
        if not any(str(fork) == 'Gnosis' for fork in forks):
            forks.append(Gnosis)
        return forks
    
    # Replace the get_forks function with our patched version
    ethereum_test_forks.helpers.get_forks = patched_get_forks
    
    # Return a dictionary representation for backward compatibility
    return {"Gnosis": Gnosis} 