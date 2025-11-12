#!/usr/bin/env python3
"""Collect metadata about all tools"""

import json
from pathlib import Path


def format_title(slug: str) -> str:
    """Convert slug to title case (e.g., 'example-tool' -> 'Example Tool')"""
    return slug.replace('-', ' ').replace('_', ' ').title()


def get_description(md_file: Path) -> str:
    """Extract description from the .md file (first non-empty line)"""
    if not md_file.exists():
        return "No description available"

    content = md_file.read_text('utf-8').strip()
    if not content:
        return "No description available"

    # Return the first non-empty line
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            return line

    return "No description available"


def gather_tools():
    tools = []

    for html_file in sorted(Path('.').glob('*.html')):
        if html_file.name == 'index.html':
            continue

        slug = html_file.stem
        md_file = Path(f'{slug}.md')

        tool = {
            'title': format_title(slug),
            'description': get_description(md_file),
            'link': f'{slug}.html',
            'slug': slug
        }

        tools.append(tool)

    with open('tools.json', 'w') as f:
        json.dump(tools, f, indent=2)

    print(f"Collected metadata for {len(tools)} tools")


if __name__ == "__main__":
    gather_tools()
