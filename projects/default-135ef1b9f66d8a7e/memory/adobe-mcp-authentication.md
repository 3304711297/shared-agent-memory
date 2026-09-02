---
name: adobe-mcp-authentication
description: Adobe for creativity MCP server requires OAuth authentication; 403
  errors indicate missing Authorization headers
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_96e5646b-aeb8-4de6-abe9-e69399637402
---

Adobe's MCP server (`https://adobe-creativity.adobe.io/mcp`) requires OAuth authentication to function. When the server returns HTTP 403 Forbidden, it typically indicates missing or invalid authentication headers.

## Authentication Requirements
- Adobe for creativity plugin marked as "🔐 Signed-In required" in skill documentation
- HTTP endpoint configuration needs `headers` field with `Authorization: Bearer <token>`
- Plugin `.mcp.json` may only contain URL without auth; requires additional configuration
- ZCode CLI requires "OAuth Native App" authentication type (not OAuth Web App or OAuth Single-Page App)

## Diagnosis Pattern
- 403 errors on MCP HTTP endpoints → check for missing authentication
- Check plugin documentation for auth requirements (look for 🔐 icons)
- Verify if Authorization header is present in MCP server configuration
- May require Adobe Creative Cloud subscription and proper OAuth flow

## Configuration Structure
```json
{
  "mcpServers": {
    "Adobe for creativity": {
      "type": "http",
      "url": "https://adobe-creativity.adobe.io/mcp",
      "headers": {
        "Authorization": "Bearer <token>"  // Required but often missing
      }
    }
  }
}
```

## OAuth Flow Selection
Adobe provides three OAuth authentication types:
- **OAuth Web App**: For applications with frontend UI and backend server (server stores secrets securely)
- **OAuth Single-Page App**: For web applications running in browser without backend server
- **OAuth Native App**: For mobile or desktop applications running natively without backend server ✅ **Choose this for ZCode CLI**

**Why OAuth Native App for ZCode CLI:**
- ZCode CLI is a desktop application running locally on the user's machine
- No backend server is involved in the authentication flow
- The native application is responsible for fetching access tokens
- Matches the architecture of local CLI tools

**Expected OAuth Native App credentials:**
- Client ID (public identifier)
- Client Secret (may not be displayed depending on configuration)
- Access Token (what goes in the Authorization header)

**Related:** [[user-windows-environment]]
