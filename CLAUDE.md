# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static website generator for a collection of web tools, hosted on GitHub Pages. The system converts markdown descriptions and standalone HTML tool files into a searchable static website with an automatically generated index page.

## Build System Architecture

The build process consists of two Python scripts that run in sequence:

1. **gather_metadata.py**: Scans all `*.html` files (except index.html), extracts metadata from corresponding `*.md` files, and generates `tools.json`
2. **build_index.py**: Reads `README.md` and `tools.json`, generates `index.html` with embedded search functionality

The build scripts are orchestrated by `build.sh`, which runs both scripts in order.

## Build Commands

```bash
# Full build (metadata + index)
source ./venv/bin/activate ./build.sh

# Or manually:
uv run python gather_metadata.py  # Generate tools.json from HTML files
uv run python build_index.py      # Generate index.html from README.md and tools.json

# Install dependencies
uv add markdown
uv sync
```

## Development Workflow

Python 3.13+ is required (specified in [pyproject.toml](pyproject.toml:6)). The project uses `uv` for dependency management and has a virtual environment at `.venv/`.

### Adding a New Tool

1. Create `tool-name.html` with the full tool implementation
2. Create `tool-name.md` with a description (first non-empty, non-heading line is used)
3. Run `./build.sh` to regenerate `tools.json` and `index.html`
4. The tool will automatically appear in the index with search functionality

Tool metadata format in `tools.json`:
```json
{
  "title": "Tool Name",        // Generated from filename
  "description": "...",         // Extracted from .md file
  "link": "tool-name.html",     // The tool file
  "slug": "tool-name"           // Filename without extension
}
```

## Key Implementation Details

- **Search Functionality**: The generated `index.html` includes embedded JavaScript that loads `tools.json` at runtime and implements client-side filtering with text highlighting
- **Markdown Processing**: The [build_index.py](build_index.py:36) script strips out the "## Tools" section from README.md and replaces it with dynamically generated HTML from `tools.json`
- **Tool Discovery**: [gather_metadata.py](gather_metadata.py:34) discovers tools by globbing for `*.html` files (excluding index.html)
- **GitHub Actions**: The [.github/workflows/deploy.yml](.github/workflows/deploy.yml) workflow builds and deploys to GitHub Pages on every push to main

## Dependencies

- `markdown>=3.10` for converting README.md to HTML (Python Markdown library with "extra" extensions enabled)
