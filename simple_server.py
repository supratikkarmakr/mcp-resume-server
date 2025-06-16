#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import fitz  # PyMuPDF

# Server configuration
server = Server("resume-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="resume",
            description="Get the user's resume in markdown format",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="validate",
            description="Validate the user's phone number",
            inputSchema={
                "type": "object", 
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "resume":
        return await get_resume()
    elif name == "validate":
        return await validate_user()
    else:
        raise ValueError(f"Unknown tool: {name}")

async def get_resume() -> list[TextContent]:
    """Get the user's resume in markdown format."""
    try:
        resume_path = Path("resume.pdf")
        
        if not resume_path.exists():
            return [TextContent(
                type="text",
                text="<error>Resume file not found. Please place your resume.pdf in the same directory as this script.</error>"
            )]
        
        doc = fitz.open(resume_path)
        text = "\n".join([page.get_text() for page in doc])
        doc.close()
        
        if text.strip():
            # Simple text to markdown conversion
            lines = text.split('\n')
            markdown_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    # Simple heuristic: if line is all caps or ends with colon, make it a header
                    if line.isupper() or line.endswith(':'):
                        markdown_lines.append(f"## {line}")
                    else:
                        markdown_lines.append(line)
                else:
                    markdown_lines.append("")
            
            return [TextContent(
                type="text",
                text='\n'.join(markdown_lines)
            )]
        else:
            return [TextContent(
                type="text",
                text="<error>No text content found in resume PDF</error>"
            )]
            
    except ImportError:
        return [TextContent(
            type="text",
            text="<error>PyMuPDF (fitz) not installed. Please install it with: pip install PyMuPDF</error>"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"<error>Could not read or convert resume: {str(e)}</error>"
        )]

async def validate_user() -> list[TextContent]:
    """Return the user's phone number for validation."""
    return [TextContent(
        type="text",
        text="917602596399"
    )]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 