#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "pydantic",
# ]
# ///
"""
FastAPI web application for serving XOR filters.

Usage:
    uv run app.py

The app will:
- Load all XOR filters from the filters/ directory
- Serve them at /router/{uuid} endpoints
- Support checking if text is in the filter
- Provide a /reload endpoint to reload filters
"""

import json
import sys
from pathlib import Path
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add current directory to path to import our custom xor_filter module
sys.path.insert(0, str(Path(__file__).parent))
from xor_filter import SimpleXorFilter


class QueryRequest(BaseModel):
    """Request model for querying the XOR filter."""
    text: str


class QueryResponse(BaseModel):
    """Response model for XOR filter queries."""
    found: bool
    uuid: str
    text: str


class ReloadResponse(BaseModel):
    """Response model for reload endpoint."""
    status: str
    filters_loaded: int
    filter_uuids: list[str]


class XORFilterApp:
    """Application class to manage XOR filters."""

    def __init__(self, filters_dir: Path = Path("filters")):
        self.filters_dir = filters_dir
        self.filters: Dict[str, SimpleXorFilter] = {}
        self.filter_metadata: Dict[str, dict] = {}
        self.load_filters()

    def load_filters(self):
        """Load all XOR filter JSON files from the filters directory."""
        self.filters.clear()
        self.filter_metadata.clear()

        if not self.filters_dir.exists():
            print(f"Warning: Filters directory '{self.filters_dir}' does not exist")
            self.filters_dir.mkdir(exist_ok=True)
            return

        json_files = list(self.filters_dir.glob("*.json"))

        if not json_files:
            print(f"Warning: No filter files found in '{self.filters_dir}'")
            return

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                filter_uuid = data["uuid"]
                filter_data = data["filter_data"]

                # Reconstruct the XOR filter from the saved data
                xor_filter = SimpleXorFilter.from_dict(filter_data)

                self.filters[filter_uuid] = xor_filter
                self.filter_metadata[filter_uuid] = {
                    "source_file": data.get("source_file"),
                    "num_entries": data.get("num_entries"),
                }

                print(f"Loaded filter {filter_uuid} ({data.get('num_entries', 0)} entries)")

            except Exception as e:
                print(f"Error loading filter from {json_file}: {e}")

        print(f"Total filters loaded: {len(self.filters)}")

    def query_filter(self, uuid: str, text: str) -> bool:
        """
        Query a filter to check if text is present.

        Args:
            uuid: UUID of the filter
            text: Text to check

        Returns:
            True if text is in the filter, False otherwise
        """
        if uuid not in self.filters:
            raise HTTPException(status_code=404, detail=f"Filter with UUID '{uuid}' not found")

        return text in self.filters[uuid]


# Initialize the filter app
filter_app = XORFilterApp()

# Create FastAPI app
app = FastAPI(
    title="XOR Filter Service",
    description="API for querying XOR filters",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "XOR Filter Service",
        "filters_loaded": len(filter_app.filters),
        "filter_uuids": list(filter_app.filters.keys())
    }


@app.post("/router/{uuid}", response_model=QueryResponse)
async def query_filter(uuid: str, request: QueryRequest):
    """
    Query a XOR filter to check if text is present.

    Args:
        uuid: UUID of the filter
        request: Query request containing the text to check

    Returns:
        QueryResponse with the result
    """
    found = filter_app.query_filter(uuid, request.text)

    return QueryResponse(
        found=found,
        uuid=uuid,
        text=request.text
    )


@app.post("/reload", response_model=ReloadResponse)
async def reload_filters():
    """
    Reload all XOR filters from the filters directory.

    This allows you to pick up new or updated filter files without restarting the server.

    Returns:
        ReloadResponse with reload status
    """
    filter_app.load_filters()

    return ReloadResponse(
        status="success",
        filters_loaded=len(filter_app.filters),
        filter_uuids=list(filter_app.filters.keys())
    )


@app.get("/filters")
async def list_filters():
    """List all loaded filters with their metadata."""
    filters_info = []
    for uuid, metadata in filter_app.filter_metadata.items():
        filters_info.append({
            "uuid": uuid,
            **metadata
        })

    return {
        "total": len(filters_info),
        "filters": filters_info
    }


def main():
    """Run the FastAPI application."""
    print("Starting XOR Filter Service...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
