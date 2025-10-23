"""
XOR Filter implementation using pyxorfilter.

A XOR filter is a probabilistic data structure for approximate membership queries.
This implementation uses the pyxorfilter library which provides efficient C-based
XOR filters that are faster and smaller than Bloom filters.
"""

import base64
from typing import List

try:
    from pyxorfilter import Xor8
except ImportError:
    raise ImportError("pyxorfilter is required. Install with: pip install pyxorfilter")


class SimpleXorFilter:
    """
    A wrapper around pyxorfilter's Xor8 implementation.

    This provides a real XOR filter implementation that is faster and more
    space-efficient than Bloom filters (~9 bits per entry).
    """

    def __init__(self, items: List[str]):
        """
        Initialize the XOR filter with a list of items.

        Args:
            items: List of strings to add to the filter
        """
        self.num_items = len(items)

        # Create and populate the Xor8 filter
        self.filter = Xor8(self.num_items)
        if not self.filter.populate(items):
            raise ValueError("Failed to populate XOR filter")

    def __contains__(self, item: str) -> bool:
        """
        Check if an item might be in the filter.

        Args:
            item: The item to check

        Returns:
            True if the item might be in the filter (or false positive),
            False if definitely not in the filter
        """
        return self.filter.contains(item)

    def to_dict(self) -> dict:
        """
        Serialize the filter to a dictionary.

        Returns:
            Dictionary representation of the filter (without items for space efficiency)
        """
        # Serialize the filter to bytes and encode as base64 for JSON compatibility
        serialized = self.filter.serialize()
        return {
            "num_items": self.num_items,
            "filter_type": "Xor8",
            "size_bytes": self.filter.size_in_bytes(),
            "data": base64.b64encode(serialized).decode('ascii')
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
        # Create a new instance and deserialize the filter
        instance = cls.__new__(cls)
        instance.num_items = data["num_items"]

        # Decode the base64 data and deserialize
        filter_bytes = base64.b64decode(data["data"])
        instance.filter = Xor8.deserialize(filter_bytes)

        return instance

    def __len__(self) -> int:
        """Return the number of items in the filter."""
        return self.num_items

    def __repr__(self) -> str:
        return f"SimpleXorFilter(items={self.num_items}, size_bytes={self.filter.size_in_bytes()})"
