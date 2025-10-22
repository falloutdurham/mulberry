#!/bin/bash
# Test script for the XOR Filter API
# Usage: ./test_api.sh <UUID>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <filter-uuid>"
    echo ""
    echo "Available filters:"
    curl -s http://localhost:8000/ | python3 -m json.tool
    exit 1
fi

UUID=$1

echo "Testing XOR Filter API"
echo "======================"
echo ""

echo "1. Testing root endpoint..."
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""

echo "2. Testing filter query (apple - should be found)..."
curl -s -X POST http://localhost:8000/router/$UUID \
    -H "Content-Type: application/json" \
    -d '{"text": "apple"}' | python3 -m json.tool
echo ""

echo "3. Testing filter query (banana - should be found)..."
curl -s -X POST http://localhost:8000/router/$UUID \
    -H "Content-Type: application/json" \
    -d '{"text": "banana"}' | python3 -m json.tool
echo ""

echo "4. Testing filter query (coconut - should NOT be found)..."
curl -s -X POST http://localhost:8000/router/$UUID \
    -H "Content-Type: application/json" \
    -d '{"text": "coconut"}' | python3 -m json.tool
echo ""

echo "5. Testing filter query (pineapple - should NOT be found)..."
curl -s -X POST http://localhost:8000/router/$UUID \
    -H "Content-Type: application/json" \
    -d '{"text": "pineapple"}' | python3 -m json.tool
echo ""

echo "6. Listing all filters..."
curl -s http://localhost:8000/filters | python3 -m json.tool
echo ""

echo "7. Testing reload endpoint..."
curl -s -X POST http://localhost:8000/reload | python3 -m json.tool
echo ""

echo "All tests completed!"
