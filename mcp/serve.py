import os
import yaml
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import redis
import json
import uvicorn

# Load configuration
with open("config.yaml") as f:
    config = yaml.safe_load(f)

app = FastAPI(title=config["meta"]["gateway_name"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config["meta"]["cors_allowed_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection for WebSocket events
if config["meta"]["websockets"]["enabled"]:
    redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))

class ToolCall(BaseModel):
    tool: str
    params: Dict[str, Any]

@app.post("/call")
async def call_tool(call: ToolCall):
    # Validate tool exists
    if call.tool not in config["tools"]:
        raise HTTPException(status_code=404, detail=f"Tool {call.tool} not found")
    
    tool_config = config["tools"][call.tool]
    
    # Build request to backend API
    method = tool_config["http"]["method"]
    path = tool_config["http"]["path"]
    
    # Format path with parameters if needed
    if "{" in path:
        try:
            path = path.format(**call.params)
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Missing path parameter: {e}")
    
    url = f"{config['meta']['backend_base_url']}{path}"
    
    # Make request to backend
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, params=call.params)
            else:
                response = await client.post(url, json=call.params)
            
            response.raise_for_status()
            result = response.json()
            
            # Handle WebSocket broadcast if configured
            if (
                config["meta"]["websockets"]["enabled"] 
                and "on_success" in tool_config 
                and "broadcast" in tool_config["on_success"]
            ):
                broadcast_config = tool_config["on_success"]["broadcast"]
                # Format payload template with response data
                payload = broadcast_config["payload_template"].format(**call.params)
                redis_client.publish(broadcast_config["topic"], payload)
            
            return result
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": config["meta"]["gateway_name"],
        "backend_url": config["meta"]["backend_base_url"]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3911))
    log_level = config["middleware"]["logging"]["level"].lower()
    uvicorn.run(app, host="0.0.0.0", port=port, log_level=log_level)
