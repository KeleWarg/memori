
import os, json
from celery import Celery
from neo4j import GraphDatabase
import openai

broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery("tasks", broker=broker_url, backend=broker_url)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "local_neo4j_pw")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

@app.task
def embed_message(message_id: str, text: str):
    if not OPENAI_API_KEY:
        return None
    embedding_resp = openai.Embedding.create(
        model="text-embedding-3-small", input=text
    )
    vector = embedding_resp["data"][0]["embedding"]
    with driver.session() as session:
        session.run(
            """
            MATCH (m {id:$msg_id})
            SET m.embedding = $vec
            """,
            msg_id=message_id,
            vec=vector,
        )
    return True
