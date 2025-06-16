# MCP Resume Server

A Model Context Protocol (MCP) server that provides resume data to Puch AI.

## Features

- **Resume Tool**: Returns formatted resume content in markdown
- **Validate Tool**: Returns phone number for validation (917602596399)
- **Bearer Token Authentication**: Uses token `3dad8ccfb378`

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python http_server.py
```

3. Server runs on `http://localhost:8085`

## Deployment Options

### Option 1: Ngrok (Current)
```
/mcp connect https://a109-2405-201-9004-913b-94ed-5a76-600e-5c98.ngrok-free.app 3dad8ccfb378
```

### Option 2: Railway
1. Push to GitHub
2. Connect to Railway
3. Deploy automatically

### Option 3: Heroku
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `git push heroku main`

## MCP Protocol

- **Endpoint**: `/mcp`
- **Method**: POST
- **Authentication**: Bearer token in Authorization header
- **Protocol**: JSON-RPC 2.0

## Tools

### resume
Returns the user's resume in markdown format.

### validate  
Returns the user's phone number: `917602596399` 