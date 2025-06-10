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
        if not rec:
            raise HTTPException(status_code=404, detail="Node not found")
        nodes = [{"id": n["id"], "label": n.get("title", n.get("text","")), "type": n["type"]} for n in rec["allNodes"]]
        links = [{"source": rel["source"], "target": rel["target"]} for rel in rec["rels"] if rel["source"] and rel["target"]]
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
