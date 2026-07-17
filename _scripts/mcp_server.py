#!/usr/bin/env python3
"""
FlowWiki MCP Server — exposes FlowWiki knowledge operations as MCP tools.

Usage:
    python _scripts/mcp_server.py                          # stdio mode (default)
    python _scripts/mcp_server.py --transport sse --port 8888  # SSE mode

Configuration:
    Add to Claude Code / Codex / Cursor MCP config:
    {
        "mcpServers": {
            "flowwiki": {
                "command": "python",
                "args": ["_scripts/mcp_server.py"],
                "cwd": "/path/to/FlowWiki"
            }
        }
    }
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Graceful fallback if mcp package is not installed
# ---------------------------------------------------------------------------
MCP_AVAILABLE = False
try:
    import mcp.server.stdio
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationCapabilities
    MCP_AVAILABLE = True
except ImportError:
    pass  # handled below; server exits with a clear message

# ---------------------------------------------------------------------------
# Optional YAML support for config parsing
# ---------------------------------------------------------------------------
try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Logging (stderr to keep stdout clean for MCP protocol)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("flowwiki-mcp")

# ---------------------------------------------------------------------------
# Project root detection
# ---------------------------------------------------------------------------
def _find_project_root() -> Path:
    """Walk up from _scripts/ to find the FlowWiki project root."""
    candidate = Path(__file__).resolve().parent.parent
    if (candidate / "SCHEMA.md").exists() and (candidate / "config.toml").exists():
        return candidate
    # Fallback: use cwd if it looks like a FlowWiki project
    cwd = Path.cwd()
    if (cwd / "SCHEMA.md").exists():
        return cwd
    raise FileNotFoundError(
        "Cannot find FlowWiki project root. "
        "Run from a FlowWiki directory or set FLOWWIKI_ROOT env var."
    )


# ═══════════════════════════════════════════════════════════════════════════
# Core helpers (read-only operations on the wiki)
# ═══════════════════════════════════════════════════════════════════════════

class FlowWikiCore:
    """Read-only (or safe-write) interface to a FlowWiki project."""

    def __init__(self, root: Path):
        self.root = root

    # ---- query -----------------------------------------------------------

    def read_index(self) -> str:
        """Return contents of wiki/index.md or a generated listing."""
        idx = self.root / "wiki" / "index.md"
        if idx.exists():
            return idx.read_text(encoding="utf-8")
        return self._generate_index()

    def search_wiki(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Simple keyword search over wiki pages (BM25-style keyword match)."""
        results: list[dict[str, Any]] = []
        query_lower = query.lower()
        wiki_dir = self.root / "wiki"
        if not wiki_dir.exists():
            return results

        for md_file in wiki_dir.rglob("*.md"):
            if md_file.name in ("README.md", "log.md"):
                continue
            if "meta" in md_file.parts:
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue
            score = content.lower().count(query_lower)
            if score > 0:
                results.append({
                    "path": str(md_file.relative_to(self.root)),
                    "title": self._extract_title(content, md_file.name),
                    "score": score,
                    "preview": content[:300].strip(),
                })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:max_results]

    def read_page(self, path: str) -> str:
        """Read a specific wiki page by relative path."""
        target = self.root / path
        if not target.exists():
            return f"# Page not found: {path}\n\nThe page does not exist yet."
        return target.read_text(encoding="utf-8")

    # ---- lint ------------------------------------------------------------

    def lint_wiki(self) -> dict[str, Any]:
        """Run health checks on the wiki."""
        issues: list[str] = []
        stats = {"pages": 0, "with_frontmatter": 0, "orphan_pages": 0, "broken_links": 0}

        wiki_dir = self.root / "wiki"
        if not wiki_dir.exists():
            return {"status": "error", "message": "wiki/ directory not found"}

        all_pages: set[str] = set()
        linked_pages: set[str] = set()

        for md_file in wiki_dir.rglob("*.md"):
            if "meta" in md_file.parts:
                continue
            stats["pages"] += 1
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            # Frontmatter check
            if content.startswith("---"):
                stats["with_frontmatter"] += 1
            else:
                issues.append(f"Missing frontmatter: {md_file.relative_to(self.root)}")

            # Collect wiki links
            rel = str(md_file.relative_to(wiki_dir))
            all_pages.add(rel)
            for line in content.splitlines():
                if "[[" in line or "](" in line:
                    linked_pages.add(rel)

        # Orphan detection: pages not linked from any other page
        stats["orphan_pages"] = len(all_pages - linked_pages - {"index.md", "log.md"})

        # Index existence
        if not (wiki_dir / "index.md").exists():
            issues.append("wiki/index.md missing")
        if not (self.root / "00_首页" / "README.md").exists():
            issues.append("00_首页/README.md missing (human UX entry)")

        return {
            "status": "warning" if issues else "healthy",
            "stats": stats,
            "issues": issues,
            "advice": (
                "Run `python _scripts/lint.py` for detailed report."
                if issues
                else "All checks passed."
            ),
        }

    # ---- research --------------------------------------------------------

    def cross_page_research(self, topic: str, max_pages: int = 20) -> dict[str, Any]:
        """Deep research across wiki pages for a topic."""
        results = self.search_wiki(topic, max_results=max_pages)
        if not results:
            return {"topic": topic, "sources": 0, "findings": [], "advice": "No matching pages found."}

        # Extract key findings
        findings: list[dict[str, Any]] = []
        for r in results:
            page_content = self.read_page(r["path"])
            findings.append({
                "page": r["title"],
                "path": r["path"],
                "relevance": r["score"],
                "snippet": r["preview"],
            })

        return {
            "topic": topic,
            "sources": len(results),
            "findings": findings,
            "advice": (
                f"Found {len(results)} relevant pages. "
                "Consider creating a comparison page in wiki/comparisons/ for cross-referencing."
            ),
        }

    # ---- utils -----------------------------------------------------------

    @staticmethod
    def _extract_title(content: str, filename: str) -> str:
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return filename.replace(".md", "").replace("-", " ").title()

    def _generate_index(self) -> str:
        """Generate a minimal index if none exists."""
        wiki_dir = self.root / "wiki"
        if not wiki_dir.exists():
            return "# Wiki Index\n\nEmpty wiki.\n"
        lines = ["# Wiki Index\n"]
        for md_file in sorted(wiki_dir.rglob("*.md")):
            rel = md_file.relative_to(wiki_dir)
            lines.append(f"- [{rel.stem}]({rel})")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# MCP Server
# ═══════════════════════════════════════════════════════════════════════════

TOOL_DEFINITIONS = [
    types.Tool(
        name="flowwiki_query",
        description=(
            "Search the FlowWiki knowledge base. "
            "Returns matching wiki pages ranked by keyword relevance. "
            "Use this for: finding concepts, looking up entities, exploring topics."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (keywords, concepts, or questions)",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 10, max: 50)",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    types.Tool(
        name="flowwiki_read",
        description=(
            "Read a specific wiki page by its relative path. "
            "Use this after flowwiki_query to drill into a relevant page."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the wiki page, e.g. 'wiki/concepts/ace.md'",
                },
            },
            "required": ["path"],
        },
    ),
    types.Tool(
        name="flowwiki_lint",
        description=(
            "Run a health check on the FlowWiki knowledge base. "
            "Detects: missing frontmatter, orphan pages, missing index, broken structure. "
            "Use this periodically to maintain wiki quality."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    types.Tool(
        name="flowwiki_research",
        description=(
            "Deep research across multiple wiki pages on a topic. "
            "Returns cross-page findings, relevance scores, and synthesis advice. "
            "Use this for: multi-document synthesis, topic exploration, comparison generation."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Research topic to investigate across the wiki",
                },
                "max_pages": {
                    "type": "integer",
                    "description": "Maximum pages to examine (default: 20)",
                    "default": 20,
                },
            },
            "required": ["topic"],
        },
    ),
    types.Tool(
        name="flowwiki_index",
        description=(
            "Read the wiki index (table of contents). "
            "Returns a listing of all wiki pages organized by category. "
            "Use this to understand the wiki structure before querying."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


def build_mcp_server(root: Path) -> Server:
    """Create and configure the MCP Server instance."""
    core = FlowWikiCore(root)

    server = Server("flowwiki-mcp")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return TOOL_DEFINITIONS

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent]:
        args = arguments or {}

        try:
            if name == "flowwiki_query":
                query = args["query"]
                max_results = min(args.get("max_results", 10), 50)
                results = core.search_wiki(query, max_results=max_results)
                output = json.dumps(results, ensure_ascii=False, indent=2)
                return [types.TextContent(type="text", text=output)]

            elif name == "flowwiki_read":
                path = args["path"]
                content = core.read_page(path)
                return [types.TextContent(type="text", text=content)]

            elif name == "flowwiki_lint":
                report = core.lint_wiki()
                output = json.dumps(report, ensure_ascii=False, indent=2)
                return [types.TextContent(type="text", text=output)]

            elif name == "flowwiki_research":
                topic = args["topic"]
                max_pages = min(args.get("max_pages", 20), 100)
                findings = core.cross_page_research(topic, max_pages=max_pages)
                output = json.dumps(findings, ensure_ascii=False, indent=2)
                return [types.TextContent(type="text", text=output)]

            elif name == "flowwiki_index":
                index_content = core.read_index()
                return [types.TextContent(type="text", text=index_content)]

            else:
                return [types.TextContent(
                    type="text",
                    text=f"Unknown tool: {name}. Available: flowwiki_query, flowwiki_read, "
                         f"flowwiki_lint, flowwiki_research, flowwiki_index",
                )]

        except Exception as exc:
            logger.exception("Tool error: %s", name)
            return [types.TextContent(
                type="text",
                text=f"Error executing {name}: {exc}",
            )]

    return server


# ═══════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════

async def run_stdio(root: Path) -> None:
    """Run the MCP server over stdio transport."""
    server = build_mcp_server(root)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationCapabilities(
                sampling={},
                experimental={},
                roots={"listChanged": True},
            ),
            notification_options=NotificationOptions(),
        )


async def main() -> None:
    if not MCP_AVAILABLE:
        print(
            "ERROR: The 'mcp' package is not installed.",
            "\nInstall it with: pip install mcp",
            "\nOr: pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    parser = argparse.ArgumentParser(description="FlowWiki MCP Server")
    parser.add_argument(
        "--root",
        help="FlowWiki project root (auto-detected if omitted)",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8888,
        help="Port for SSE transport (default: 8888)",
    )
    args = parser.parse_args()

    root = Path(args.root) if args.root else _find_project_root()
    logger.info("FlowWiki MCP Server starting | root=%s | transport=%s", root, args.transport)

    if args.transport == "stdio":
        await run_stdio(root)
    else:
        # SSE mode (optional, for web-based agents)
        try:
            from mcp.server.sse import SseServerTransport
            from starlette.applications import Starlette
            from starlette.routing import Route
            import uvicorn

            server = build_mcp_server(root)
            sse = SseServerTransport("/messages/")

            async def handle_sse(request):
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    await server.run(
                        streams[0],
                        streams[1],
                        server.create_initialization_options(),
                    )

            app = Starlette(
                routes=[
                    Route("/sse", endpoint=handle_sse),
                ]
            )
            config = uvicorn.Config(app, host="0.0.0.0", port=args.port, log_level="info")
            srv = uvicorn.Server(config)
            await srv.serve()
        except ImportError:
            logger.error(
                "SSE mode requires: pip install mcp[cli] uvicorn starlette"
            )
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
