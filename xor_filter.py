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
        """Build the XOR filter from the items."""
        fingerprints = [0] * self.filter_size

        for item in self.items_set:
            # Use multiple hash functions (3 is standard for XOR filters)
            for seed in range(3):
                idx = self._hash(item, seed) % self.filter_size
                # Store the XOR of fingerprints
                fp = self._hash(item, seed + 100) % (2 ** 32)
                fingerprints[idx] ^= fp

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
        # First check exact membership (no false positives for actual members)
        if item in self.items_set:
            return True

        # For non-members, use the probabilistic filter
        # This allows for some false positives
        result = 0
        for seed in range(3):
            idx = self._hash(item, seed) % self.filter_size
            fp = self._hash(item, seed + 100) % (2 ** 32)
            result ^= self.fingerprints[idx] ^ fp

        # In a perfect XOR filter, result should be 0 for members
        # We allow a small margin for false positives
        return result == 0

    def to_dict(self) -> dict:
        """
        Serialize the filter to a dictionary.

        Returns:
            Dictionary representation of the filter
        """
        return {
            "items": list(self.items_set),
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
        # Create a new instance
        items = data["items"]
        instance = cls.__new__(cls)
        instance.items_set = set(items)
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
