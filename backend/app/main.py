import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from neo4j.exceptions import ServiceUnavailable
from .db import get_session
from .schemas import *
from .graph.utils import create_conversation, add_message

app = FastAPI(title="Graph Memory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Graph Memory API"}

@app.post("/seed")
def create_sample_data():
    """Create sample data for testing."""
    # Create a sample conversation
    conv_id = create_conversation("Sample Conversation")
    
    # Add some sample messages
    msg1_id = add_message(conv_id, "user", "Hello, can you help me with graph databases?")
    msg2_id = add_message(conv_id, "assistant", "Of course! Graph databases are great for storing connected data. They use nodes and relationships to represent information.")
    msg3_id = add_message(conv_id, "user", "What are the benefits of using Neo4j?")
    msg4_id = add_message(conv_id, "assistant", "Neo4j offers powerful query language (Cypher), ACID compliance, scalability, and excellent visualization tools.")
    
    return {
        "conversation_id": conv_id,
        "message_ids": [msg1_id, msg2_id, msg3_id, msg4_id],
        "status": "Sample data created successfully"
    }

def session_dep():
    with get_session() as s:
        yield s

@app.post("/conversations", response_model=str)
def create_conv(payload: ConversationCreate):
    return create_conversation(payload.title)

@app.post("/messages", response_model=str)
def add_msg(payload: MessageCreate):
    msg_id = add_message(payload.conversation_id, payload.role, payload.text)
    return msg_id

@app.get("/conversations", response_model=list)
def get_conversations(session=Depends(session_dep)):
    """Get all conversations."""
    query = """
    MATCH (c:Conversation)
    RETURN c
    ORDER BY c.created_at DESC
    """
    try:
        result = session.run(query)
        conversations = []
        for record in result:
            conv = dict(record["c"])
            conversations.append(conv)
        return conversations
    except ServiceUnavailable as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nodes/{node_id}/children", response_model=GraphData)
def children(node_id: str, depth: int = Query(1, ge=1, le=3), session=Depends(session_dep)):
    q_nodes = f"""
    MATCH (n {{id:$id}})-[*1..{depth}]-(c)
    WITH collect(distinct n)+collect(distinct c) as nodes
    UNWIND nodes as x
    OPTIONAL MATCH (x)-[r]->(y)
    RETURN collect(distinct x) as allNodes, collect(distinct {{source: startNode(r).id, target: endNode(r).id}}) as rels
    """
    try:
        rec = session.run(q_nodes, id=node_id).single()
        if not rec or not rec["allNodes"]:
            # If no node found, return empty graph
            return {"nodes": [], "links": []}
        nodes = [{"id": n["id"], "label": n.get("title", n.get("text",""))[:50], "type": n["type"]} for n in rec["allNodes"] if n]
        links = [{"source": rel["source"], "target": rel["target"]} for rel in rec["rels"] if rel and rel["source"] and rel["target"]]
        return {"nodes": nodes, "links": links}
    except ServiceUnavailable as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_model=GraphData)
def search(q: str, k: int = 5, session=Depends(session_dep)):
    # Placeholder until embeddings indexed
    query = """
    MATCH (n:Message)
    WHERE n.text CONTAINS $q
    RETURN n LIMIT $k
    """
    recs = session.run(query, q=q, k=k)
    nodes = []
    links = []
    for r in recs:
        n = r["n"]
        nodes.append({"id": n["id"], "label": n["text"], "type": n["type"]})
    return {"nodes": nodes, "links": links}
