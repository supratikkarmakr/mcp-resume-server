import requests
import json

def test_mcp_server():
    """Test the MCP server endpoints."""
    base_url = "http://localhost:8085"
    headers = {
        "Authorization": "Bearer 3dad8ccfb378",
        "Content-Type": "application/json"
    }
    
    print("Testing MCP Server...")
    print("=" * 50)
    
    # Test 1: List tools
    print("1. Testing tools/list...")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        response = requests.post(f"{base_url}/mcp", headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Test 2: Call resume tool
    print("2. Testing resume tool...")
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "resume",
            "arguments": {}
        }
    }
    
    try:
        response = requests.post(f"{base_url}/mcp", headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            content = data.get("result", {}).get("content", [])
            if content:
                print("Resume content received successfully!")
                print(f"Length: {len(content[0].get('text', ''))} characters")
            else:
                print("No content received")
        else:
            print(f"Response: {response.text}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Test 3: Call validate tool
    print("3. Testing validate tool...")
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "validate",
            "arguments": {}
        }
    }
    
    try:
        response = requests.post(f"{base_url}/mcp", headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            content = data.get("result", {}).get("content", [])
            if content:
                print(f"Validation result: {content[0].get('text', '')}")
            else:
                print("No content received")
        else:
            print(f"Response: {response.text}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

if __name__ == "__main__":
    test_mcp_server() 