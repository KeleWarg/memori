
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
from starlette.responses import JSONResponse

app = FastAPI(title="MCP Agent Stub")

class ToolCall(BaseModel):
    tool: str
    params: Dict[str, Any]

@app.post("/call")
def call_tool(call: ToolCall):
    # Stub forwarder: in real impl, proxy to FastAPI API
    return JSONResponse({"status": "ok", "echo": call.dict()})
