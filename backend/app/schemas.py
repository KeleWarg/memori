"""Pydantic schemas for the Graph Memory API."""

from pydantic import BaseModel
from typing import List, Optional


class ConversationCreate(BaseModel):
    title: str


class MessageCreate(BaseModel):
    conversation_id: str
    role: str  # "user" or "assistant"
    text: str


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphLink(BaseModel):
    source: str
    target: str


class GraphData(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    text: str
    timestamp: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None 