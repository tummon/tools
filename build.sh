#!/bin/bash
set -e

echo "=== Building tools website ==="

echo "Gathering tool metadata..."
python3 gather_metadata.py

echo "Converting README.md to index.html..."
python3 build_index.py

echo "=== Build complete! ==="
