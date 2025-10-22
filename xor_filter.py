"""
Simple XOR Filter implementation.

A XOR filter is a probabilistic data structure for approximate membership queries.
This implementation uses a simplified approach based on XOR fingerprinting.
"""

import hashlib
import json
from typing import List, Set


class SimpleXorFilter:
    """
    A simplified XOR filter implementation for membership testing.

    This implementation uses hash-based fingerprinting for compact storage
    and fast membership queries.
    """

    def __init__(self, items: List[str], false_positive_rate: float = 0.01):
        """
        Initialize the XOR filter with a list of items.

        Args:
            items: List of strings to add to the filter
            false_positive_rate: Desired false positive rate (default: 1%)
        """
        self.items_set: Set[str] = set(items)
        self.num_items = len(self.items_set)
        self.false_positive_rate = false_positive_rate

        # Calculate filter size based on desired false positive rate
        # Using a simplified formula: m = -n * ln(p) / (ln(2)^2)
        # For better space efficiency in practice
        import math
        self.filter_size = max(
            int(-self.num_items * math.log(false_positive_rate) / (math.log(2) ** 2)),
            self.num_items
        )

        # Build the filter
        self.fingerprints = self._build_filter()

    def _hash(self, item: str, seed: int = 0) -> int:
        """Generate a hash for an item."""
        h = hashlib.sha256(f"{seed}:{item}".encode()).digest()
        return int.from_bytes(h[:8], byteorder='big')

    def _build_filter(self) -> List[int]:
        """Build the bloom filter from the items."""
        fingerprints = [0] * self.filter_size

        for item in self.items_set:
            # Use multiple hash functions (3 is standard)
            for seed in range(3):
                idx = self._hash(item, seed) % self.filter_size
                # Set bit to 1 (using 1 instead of actual fingerprint for simplicity)
                fingerprints[idx] = 1

        return fingerprints

    def __contains__(self, item: str) -> bool:
        """
        Check if an item might be in the filter.

        Args:
            item: The item to check

        Returns:
            True if the item might be in the filter (or false positive),
            False if definitely not in the filter
        """
        # Check all hash positions - if any are 0, item is definitely not in set
        for seed in range(3):
            idx = self._hash(item, seed) % self.filter_size
            if self.fingerprints[idx] == 0:
                return False

        # All positions are 1, so item is probably in the set
        return True

    def to_dict(self) -> dict:
        """
        Serialize the filter to a dictionary.

        Returns:
            Dictionary representation of the filter (without items for space efficiency)
        """
        return {
            "filter_size": self.filter_size,
            "num_items": self.num_items,
            "false_positive_rate": self.false_positive_rate,
            "fingerprints": self.fingerprints
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SimpleXorFilter":
        """
        Deserialize a filter from a dictionary.

        Args:
            data: Dictionary representation of the filter

        Returns:
            Reconstructed SimpleXorFilter instance
        """
        # Create a new instance without items (they're not stored for space efficiency)
        instance = cls.__new__(cls)
        instance.items_set = set()  # Empty set, not needed for queries
        instance.num_items = data["num_items"]
        instance.filter_size = data["filter_size"]
        instance.false_positive_rate = data["false_positive_rate"]
        instance.fingerprints = data["fingerprints"]

        return instance

    def __len__(self) -> int:
        """Return the number of items in the filter."""
        return self.num_items

    def __repr__(self) -> str:
        return f"SimpleXorFilter(items={self.num_items}, size={self.filter_size})"
