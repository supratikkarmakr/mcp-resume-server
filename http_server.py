#!/usr/bin/env python3
import asyncio
import json
import os
from pathlib import Path
from aiohttp import web, web_request
import fitz  # PyMuPDF
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_resume():
    """Get the user's resume in markdown format."""
    try:
        resume_path = Path("resume.pdf")
        
        if not resume_path.exists():
            return "<error>Resume file not found. Please place your resume.pdf in the same directory as this script.</error>"
        
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
            
            return '\n'.join(markdown_lines)
        else:
            return "<error>No text content found in resume PDF</error>"
            
    except ImportError:
        return "<error>PyMuPDF (fitz) not installed. Please install it with: pip install PyMuPDF</error>"
    except Exception as e:
        return f"<error>Could not read or convert resume: {str(e)}</error>"

async def validate_user():
    """Return the user's phone number for validation."""
    return "917602596399"

async def handle_mcp_request(request: web_request.Request):
    """Handle MCP protocol requests."""
    logger.info(f"MCP request from {request.remote}: {request.method} {request.path}")
    
    # Check authentication
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer 3dad8ccfb378'):
        logger.warning(f"Unauthorized request: {auth_header}")
        return web.json_response(
            {"error": "Unauthorized"}, 
            status=401
        )
    
    try:
        data = await request.json()
        logger.info(f"MCP request data: {data}")
    except:
        logger.error("Invalid JSON in request")
        return web.json_response(
            {"error": "Invalid JSON"}, 
            status=400
        )
    
    # Handle different MCP methods
    method = data.get('method', '')
    request_id = data.get('id', 1)
    
    if method == 'initialize':
        # Initialize MCP connection
        params = data.get('params', {})
        client_info = params.get('clientInfo', {})
        protocol_version = params.get('protocolVersion', '2024-11-05')
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "logging": {}
                },
                "serverInfo": {
                    "name": "mcp-resume-server",
                    "version": "1.0.0"
                }
            }
        }
        logger.info(f"MCP initialized with client: {client_info.get('name', 'unknown')}")
        return web.json_response(response)
    
    elif method == 'tools/list':
        # List available tools
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "resume",
                        "description": "Get the user's resume in markdown format",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "validate", 
                        "description": "Validate the user's phone number",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                ]
            }
        }
        logger.info("Returning tools list")
        return web.json_response(response)
    
    elif method == 'tools/call':
        # Call a specific tool
        params = data.get('params', {})
        tool_name = params.get('name', '')
        logger.info(f"Calling tool: {tool_name}")
        
        if tool_name == 'resume':
            result = await get_resume()
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            logger.info(f"Resume tool returned {len(result)} characters")
            return web.json_response(response)
            
        elif tool_name == 'validate':
            result = await validate_user()
            response = {
                "jsonrpc": "2.0", 
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            logger.info(f"Validate tool returned: {result}")
            return web.json_response(response)
        
        else:
            logger.error(f"Unknown tool: {tool_name}")
            return web.json_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                },
                status=400
            )
    
    else:
        logger.error(f"Unknown method: {method}")
        return web.json_response(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            },
            status=400
        )

async def handle_root(request: web_request.Request):
    """Handle root requests - provide helpful information."""
    logger.info(f"Root request from {request.remote}: {request.method} {request.path}")
    
    # Return helpful information about the MCP server
    info = {
        "server": "MCP Resume Server",
        "version": "1.0",
        "endpoints": {
            "/mcp": "MCP protocol endpoint (POST only)",
            "/": "This information endpoint"
        },
        "tools": ["resume", "validate"],
        "authentication": "Bearer token required",
        "protocol": "JSON-RPC 2.0"
    }
    
    # Add ngrok skip header to response
    response = web.json_response(info)
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

async def handle_any_path(request: web_request.Request):
    """Handle any other path requests."""
    logger.info(f"Unknown path request from {request.remote}: {request.method} {request.path}")
    
    response = web.json_response(
        {
            "error": "Not Found",
            "message": f"Path '{request.path}' not found. Use '/mcp' for MCP protocol requests.",
            "available_endpoints": ["/", "/mcp"]
        }, 
        status=404
    )
    # Add ngrok skip header to response
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

def create_app():
    """Create the web application."""
    app = web.Application()
    
    # MCP endpoint
    app.router.add_post('/mcp', handle_mcp_request)
    
    # Root endpoint
    app.router.add_get('/', handle_root)
    app.router.add_post('/', handle_root)
    
    # Catch-all for any other paths
    app.router.add_route('*', '/{path:.*}', handle_any_path)
    
    return app

async def main():
    """Run the HTTP server."""
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Use PORT environment variable for cloud deployment, fallback to 8085
    port = int(os.environ.get('PORT', 8085))
    
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"MCP Server running on http://0.0.0.0:{port}")
    logger.info("Available tools: resume, validate")
    logger.info("MCP endpoint: /mcp")
    logger.info("Bearer token: 3dad8ccfb378")
    if port == 8085:
        logger.info("Ngrok URL: https://a109-2405-201-9004-913b-94ed-5a76-600e-5c98.ngrok-free.app")
    
    # Keep the server running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 