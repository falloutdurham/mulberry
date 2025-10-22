# XOR Filter Application

A FastAPI-based web service for querying XOR filters. This application consists of two main components:

1. **Training Script** (`train.py`) - Builds XOR filters from text files
2. **Web Service** (`app.py`) - Serves the filters via a REST API

## Features

- Build XOR filters from text files (one entry per line)
- Serve multiple filters via REST API
- Query filters to check membership
- Hot-reload filters without restarting the service
- Uses inline `uv` dependencies for easy execution

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

## Usage

### 1. Build a XOR Filter

Create a text file with one entry per line, then build the filter:

```bash
uv run train.py example_data.txt
```

This will:
- Read all lines from the input file
- Build a XOR filter
- Generate a UUID for the filter
- Save it as `filters/{uuid}.json`

### 2. Start the Web Service

```bash
uv run app.py
```

The service will start on `http://localhost:8000` and automatically load all filters from the `filters/` directory.

### 3. API Endpoints

#### GET `/`
Get service information and list of loaded filters.

```bash
curl http://localhost:8000/
```

#### POST `/router/{uuid}`
Query a filter to check if text is present.

**Request:**
```bash
curl -X POST http://localhost:8000/router/{uuid} \
  -H "Content-Type: application/json" \
  -d '{"text": "apple"}'
```

**Response:**
```json
{
  "found": true,
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "text": "apple"
}
```

#### POST `/reload`
Reload all filters from the `filters/` directory without restarting the service.

```bash
curl -X POST http://localhost:8000/reload
```

**Response:**
```json
{
  "status": "success",
  "filters_loaded": 2,
  "filter_uuids": ["uuid1", "uuid2"]
}
```

#### GET `/filters`
List all loaded filters with their metadata.

```bash
curl http://localhost:8000/filters
```

## Example Workflow

1. Create a filter from the example data:
   ```bash
   uv run train.py example_data.txt
   ```

2. Note the UUID from the output (e.g., `abc123...`)

3. Start the web service:
   ```bash
   uv run app.py
   ```

4. In another terminal, query the filter:
   ```bash
   # Should return found: true
   curl -X POST http://localhost:8000/router/abc123... \
     -H "Content-Type: application/json" \
     -d '{"text": "apple"}'

   # Should return found: false
   curl -X POST http://localhost:8000/router/abc123... \
     -H "Content-Type: application/json" \
     -d '{"text": "coconut"}'
   ```

5. Add more filters and reload:
   ```bash
   uv run train.py another_file.txt
   curl -X POST http://localhost:8000/reload
   ```

## How XOR Filters Work

XOR filters are a space-efficient probabilistic data structure for approximate membership queries. They offer:

- **Fast lookups** - O(1) membership testing
- **Compact size** - ~9.84 bits per key
- **No false negatives** - If an item is in the set, the filter will always return true
- **Small false positive rate** - ~0.39% chance of false positives

They're ideal for use cases where you need to quickly check if an item exists in a large set with minimal memory overhead.

## Directory Structure

```
.
├── train.py            # Training script to build XOR filters
├── app.py              # FastAPI web service
├── example_data.txt    # Example input data
├── filters/            # Directory containing filter JSON files
│   └── {uuid}.json    # Individual filter files
└── README.md           # This file
```

## API Documentation

Once the service is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
