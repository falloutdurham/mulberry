#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Training script for XOR filters.

Usage:
    uv run train.py <input_file.txt>

This will create a JSON file with the XOR filter in the filters/ directory.
"""

import argparse
import json
import sys
import uuid
from pathlib import Path

# Add current directory to path to import our custom xor_filter module
sys.path.insert(0, str(Path(__file__).parent))
from xor_filter import SimpleXorFilter


def build_xor_filter(input_file: Path, output_dir: Path = Path("filters")):
    """
    Build a XOR filter from a text file where each line is an entry.

    Args:
        input_file: Path to the input text file
        output_dir: Directory to save the filter JSON files
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Read all lines from the input file
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print(f"Error: No data found in {input_file}")
        return

    print(f"Building XOR filter with {len(lines)} entries...")

    # Build the XOR filter
    xor_filter = SimpleXorFilter(lines)

    # Generate a UUID for this filter
    filter_uuid = str(uuid.uuid4())

    # Serialize the filter
    filter_data = {
        "uuid": filter_uuid,
        "source_file": str(input_file),
        "num_entries": len(lines),
        "filter_data": xor_filter.to_dict()
    }

    # Save to JSON file
    output_file = output_dir / f"{filter_uuid}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filter_data, f, indent=2)

    print(f"XOR filter created successfully!")
    print(f"UUID: {filter_uuid}")
    print(f"Output file: {output_file}")
    print(f"Entries: {len(lines)}")


def main():
    parser = argparse.ArgumentParser(description="Build XOR filter from text file")
    parser.add_argument("input_file", type=Path, help="Input text file (one entry per line)")
    parser.add_argument("--output-dir", type=Path, default=Path("filters"),
                       help="Output directory for filter JSON files (default: filters/)")

    args = parser.parse_args()

    if not args.input_file.exists():
        print(f"Error: Input file '{args.input_file}' does not exist")
        return 1

    build_xor_filter(args.input_file, args.output_dir)
    return 0


if __name__ == "__main__":
    exit(main())
