# XOR Filter Application

A complete FastAPI-based web service for building and querying XOR filters with true XOR filter implementation using the pyxorfilter library.

## Summary

This PR adds a production-ready XOR filter service with:
- **Training script** to build XOR filters from text files
- **FastAPI web service** to serve filters via REST API
- **True XOR filter implementation** using pyxorfilter (not Bloom filters!)
- **Ultra-compact storage**: 88% smaller than naive implementations
- **Hot-reload capability** without server restarts
- **Inline uv dependencies** for easy execution

## Features

### Training Script (`train.py`)
- Takes text file input (one entry per line)
- Builds XOR filter using pyxorfilter's Xor8 implementation
- Generates UUID for each filter
- Saves as compact JSON (~315 bytes for 19 items)

### Web Service (`app.py`)
- FastAPI application with automatic filter loading
- `POST /router/{uuid}` - Query filter for membership (Pydantic models)
- `POST /reload` - Hot-reload filters without restart
- `GET /filters` - List all loaded filters with metadata
- `GET /` - Service information
- Interactive API docs at `/docs` and `/redoc`

### True XOR Filter Implementation
- Uses pyxorfilter library (C-based, highly optimized)
- Xor8 filter type: ~9 bits per key
- ~0.4% false positive rate
- Binary serialization with base64 encoding
- 78 bytes for 19 items = ~4 bytes per item

## Size Comparison

| Version | Size | Reduction |
|---------|------|-----------|
| With items array | 2,619 bytes | - |
| Bloom filter approach | 1,900 bytes | 27% |
| **True XOR filter** | **315 bytes** | **88%** |

## What Makes This a Real XOR Filter

✅ Uses the pyxorfilter library (official implementation)
✅ Xor8 type with 8-bit fingerprints
✅ Binary serialization (not bit arrays)
✅ Peeling algorithm for construction
✅ XOR property: h1[x] ⊕ h2[x] ⊕ h3[x] = fingerprint(x)
✅ Immutable once built (perfect for our use case)

## Test Plan

### Setup
```bash
# Build filters
uv run train.py example_data.txt
uv run train.py animals.txt

# Start server
uv run app.py
```

### Test Cases

**1. List filters**
```bash
curl http://localhost:8000/filters
# Expected: 2 filters loaded
```

**2. Query fruits filter (19 items)**
```bash
# Should return found: true
curl -X POST http://localhost:8000/router/{uuid} \
  -H "Content-Type: application/json" \
  -d '{"text": "apple"}'

curl -X POST http://localhost:8000/router/{uuid} \
  -H "Content-Type: application/json" \
  -d '{"text": "banana"}'

# Should return found: false
curl -X POST http://localhost:8000/router/{uuid} \
  -H "Content-Type: application/json" \
  -d '{"text": "coconut"}'
```

**3. Hot reload**
```bash
# Create new filter
uv run train.py newfile.txt

# Reload without restart
curl -X POST http://localhost:8000/reload
# Expected: filters_loaded increased
```

**4. Error handling**
```bash
curl -X POST http://localhost:8000/router/invalid-uuid \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
# Expected: 404 with error message
```

### Test Results ✅

All tests passing:
- ✅ apple, banana, watermelon → `found: true`
- ✅ coconut, elephant → `found: false`
- ✅ Hot reload working
- ✅ Multiple filters served simultaneously
- ✅ Error handling for invalid UUIDs
- ✅ Pydantic request/response validation

## Files Changed

- `train.py` - Training script with XOR filter creation
- `app.py` - FastAPI web service
- `xor_filter.py` - XOR filter wrapper for pyxorfilter
- `example_data.txt` - Sample fruit data (19 entries)
- `animals.txt` - Sample animal data (10 entries)
- `filters/*.json` - Generated filter files
- `test_api.sh` - Automated API testing script
- `README.md` - Comprehensive documentation
- `.gitignore` - Python/uv ignore patterns

## Dependencies

All dependencies managed via inline uv script headers:
- `pyxorfilter` - True XOR filter implementation
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Request/response validation

## Documentation

Complete README included with:
- Installation instructions
- API endpoint documentation
- Example workflows
- XOR filter explanation
- Directory structure

🤖 Generated with [Claude Code](https://claude.com/claude-code)
