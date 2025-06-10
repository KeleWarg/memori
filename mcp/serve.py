
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
from starlette.responses import JSONResponse
import uvicorn
import os

app = FastAPI(title="MCP Agent Stub")

class ToolCall(BaseModel):
    tool: str
    params: Dict[str, Any]

@app.post("/call")
def call_tool(call: ToolCall):
    # Stub forwarder: in real impl, proxy to FastAPI API
    return JSONResponse({"status": "ok", "echo": call.dict()})

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3911))
    uvicorn.run(app, host="0.0.0.0", port=port)
