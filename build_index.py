#!/usr/bin/env python3
"""Generate index.html from README.md with search functionality"""

import json
from pathlib import Path

try:
    import markdown
except ModuleNotFoundError as exc:
    raise SystemExit(
        "The 'markdown' package is required. "
        "Install it with 'pip install markdown'."
    ) from exc

README_PATH = Path("README.md")
OUTPUT_PATH = Path("index.html")
TOOLS_JSON_PATH = Path("tools.json")


def build_index():
    if not README_PATH.exists():
        raise FileNotFoundError("README.md not found")

    # Load tools data
    tools = []
    if TOOLS_JSON_PATH.exists():
        tools = json.loads(TOOLS_JSON_PATH.read_text("utf-8"))

    markdown_content = README_PATH.read_text("utf-8")
    md = markdown.Markdown(extensions=["extra"])
    body_html = md.convert(markdown_content)

    # Generate tools list HTML from tools.json if available
    tools_list_html = ""
    if tools:
        tools_list_html = "<h2>Tools</h2>\n<ul>\n"
        for tool in tools:
            tools_list_html += f'  <li><a href="{tool["link"]}">{tool["title"]}</a> - {tool["description"]}</li>\n'
        tools_list_html += "</ul>\n"

    # Replace the Tools section in body_html if it exists
    # Otherwise append the tools list
    if "## Tools" in markdown_content or "<h2>Tools</h2>" in body_html:
        # Find and replace the tools section
        import re
        # Remove any existing tools section (h2 Tools and following ul)
        body_html = re.sub(
            r'<h2>Tools</h2>.*?</ul>',
            tools_list_html.strip(),
            body_html,
            flags=re.DOTALL
        )
    elif tools_list_html:
        body_html += "\n" + tools_list_html

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Tools Collection</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 980px;
            margin: 0 auto;
            padding: 20px;
            color: #24292e;
        }}
        h1 {{
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        h2 {{
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
            margin-top: 24px;
        }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}

        /* Search box styling */
        .search-container {{
            margin: 20px 0;
            position: sticky;
            top: 0;
            background: white;
            padding: 10px 0;
            z-index: 100;
        }}

        #searchInput {{
            width: 100%;
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            transition: border-color 0.3s;
        }}

        #searchInput:focus {{
            outline: none;
            border-color: #0366d6;
        }}

        .search-hint {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}

        /* Hide items that don't match search */
        .tool-item.hidden {{
            display: none;
        }}

        .no-results {{
            display: none;
            padding: 20px;
            text-align: center;
            color: #666;
            font-style: italic;
        }}

        .no-results.visible {{
            display: block;
        }}

        /* Highlight matching text */
        .highlight {{
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 2px;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
{body_html}

<script>
(function() {{
    'use strict';

    let toolsData = [];

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', init);
    }} else {{
        init();
    }}

    function init() {{
        // Load tools.json
        fetch('tools.json')
            .then(response => response.json())
            .then(data => {{
                toolsData = data;
                initSearch();
            }})
            .catch(error => {{
                console.error('Failed to load tools.json:', error);
                initSearch(); // Initialize anyway with fallback
            }});
    }}

    function initSearch() {{
        // Find the tools list (look for h2 with "Tools" followed by ul)
        const headings = document.querySelectorAll('h2');
        let toolsList = null;

        for (const heading of headings) {{
            if (heading.textContent.toLowerCase().includes('tool')) {{
                toolsList = heading.nextElementSibling;
                while (toolsList && toolsList.tagName !== 'UL') {{
                    toolsList = toolsList.nextElementSibling;
                }}
                if (toolsList) {{
                    // Add search box before the tools list
                    const searchContainer = document.createElement('div');
                    searchContainer.className = 'search-container';
                    searchContainer.innerHTML = `
                        <input type="text" id="searchInput" placeholder="Search tools..." aria-label="Search tools">
                        <div class="search-hint">Type to filter tools by name or description</div>
                    `;
                    heading.parentNode.insertBefore(searchContainer, heading.nextSibling);

                    // Add no results message
                    const noResults = document.createElement('div');
                    noResults.className = 'no-results';
                    noResults.textContent = 'No tools match your search.';
                    toolsList.parentNode.insertBefore(noResults, toolsList.nextSibling);

                    // Mark all list items as tool items and associate with tool data
                    const items = toolsList.querySelectorAll('li');
                    items.forEach((item, index) => {{
                        item.classList.add('tool-item');
                        item.dataset.originalHtml = item.innerHTML;
                        if (toolsData[index]) {{
                            item.dataset.toolData = JSON.stringify(toolsData[index]);
                        }}
                    }});

                    // Set up search functionality
                    const searchInput = document.getElementById('searchInput');
                    searchInput.addEventListener('input', function() {{
                        filterTools(this.value, toolsList, noResults);
                    }});

                    break;
                }}
            }}
        }}
    }}

    function filterTools(searchTerm, toolsList, noResults) {{
        const items = toolsList.querySelectorAll('.tool-item');
        const term = searchTerm.toLowerCase().trim();
        let visibleCount = 0;

        items.forEach(item => {{
            // Reset to original HTML to clear previous highlights
            item.innerHTML = item.dataset.originalHtml;

            let matches = false;

            // Search in tool data if available
            if (item.dataset.toolData) {{
                try {{
                    const tool = JSON.parse(item.dataset.toolData);
                    const searchableText = `${{tool.title}} ${{tool.description}}`.toLowerCase();
                    matches = term === '' || searchableText.includes(term);
                }} catch (e) {{
                    // Fallback to text content
                    matches = term === '' || item.textContent.toLowerCase().includes(term);
                }}
            }} else {{
                // Fallback to text content
                matches = term === '' || item.textContent.toLowerCase().includes(term);
            }}

            if (matches) {{
                item.classList.remove('hidden');
                visibleCount++;

                // Highlight matching text if there's a search term
                if (term !== '') {{
                    highlightText(item, term);
                }}
            }} else {{
                item.classList.add('hidden');
            }}
        }});

        // Show/hide no results message
        if (visibleCount === 0 && term !== '') {{
            noResults.classList.add('visible');
        }} else {{
            noResults.classList.remove('visible');
        }}
    }}

    function highlightText(element, searchTerm) {{
        // Get all text nodes and highlight matches
        const walk = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const nodesToReplace = [];
        let node;

        while (node = walk.nextNode()) {{
            const text = node.textContent;
            const lowerText = text.toLowerCase();
            const index = lowerText.indexOf(searchTerm);

            if (index !== -1) {{
                nodesToReplace.push({{
                    node: node,
                    text: text,
                    index: index
                }});
            }}
        }}

        // Replace text nodes with highlighted versions
        nodesToReplace.forEach(item => {{
            const before = item.text.substring(0, item.index);
            const match = item.text.substring(item.index, item.index + searchTerm.length);
            const after = item.text.substring(item.index + searchTerm.length);

            const span = document.createElement('span');
            span.innerHTML = before + '<span class="highlight">' + match + '</span>' + after;

            item.node.parentNode.replaceChild(span, item.node);
        }});
    }}
}})();
</script>
</body>
</html>
"""

    OUTPUT_PATH.write_text(full_html, "utf-8")
    print("index.html created successfully with search functionality")


if __name__ == "__main__":
    build_index()
