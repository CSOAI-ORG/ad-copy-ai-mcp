<div align="center">

# Ad Copy Ai MCP

**MCP server for ad copy ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-ad-copy-ai-mcp)](https://pypi.org/project/meok-ad-copy-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Ad Copy Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `generate_ad_copy` | Generate ad copy for a platform |
| `generate_variants` | Generate multiple ad variants for A/B testing |
| `create_campaign` | Create an ad campaign |
| `get_campaign` | Get campaign details |
| `add_creative` | Add a creative to campaign |
| `get_performance` | Get creative performance metrics |
| `optimize_copy` | Optimize existing copy based on performance |
| `generate_headlines` | Generate multiple headlines |
| `get_best_performing` | Get best performing creatives |

## Installation

```bash
pip install meok-ad-copy-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ad-copy-ai": {
      "command": "python",
      "args": ["-m", "meok_ad_copy_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 9 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
