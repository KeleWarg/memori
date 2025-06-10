"""Graph database utilities for managing conversations and messages."""

import uuid
from datetime import datetime
from ..db import get_session


def create_conversation(title: str) -> str:
    """Create a new conversation node in the graph."""
    conversation_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    with get_session() as session:
        query = """
        CREATE (c:Conversation {
            id: $id,
            title: $title,
            created_at: $timestamp,
            updated_at: $timestamp,
            type: 'conversation'
        })
        RETURN c.id as id
        """
        result = session.run(query, id=conversation_id, title=title, timestamp=timestamp)
        record = result.single()
        return record["id"] if record else conversation_id


def add_message(conversation_id: str, role: str, text: str) -> str:
    """Add a message to a conversation and create relationships."""
    message_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    with get_session() as session:
        # Create the message node
        query = """
        MATCH (c:Conversation {id: $conv_id})
        CREATE (m:Message {
            id: $msg_id,
            conversation_id: $conv_id,
            role: $role,
            text: $text,
            timestamp: $timestamp,
            type: 'message'
        })
        CREATE (c)-[:HAS_MESSAGE]->(m)
        SET c.updated_at = $timestamp
        RETURN m.id as id
        """
        result = session.run(
            query,
            conv_id=conversation_id,
            msg_id=message_id,
            role=role,
            text=text,
            timestamp=timestamp
        )
        record = result.single()
        return record["id"] if record else message_id


def get_conversation_messages(conversation_id: str) -> list:
    """Get all messages for a conversation."""
    with get_session() as session:
        query = """
        MATCH (c:Conversation {id: $conv_id})-[:HAS_MESSAGE]->(m:Message)
        RETURN m
        ORDER BY m.timestamp ASC
        """
        result = session.run(query, conv_id=conversation_id)
        messages = []
        for record in result:
            message = dict(record["m"])
            messages.append(message)
        return messages


def search_messages(query_text: str, limit: int = 10) -> list:
    """Search for messages containing the query text."""
    with get_session() as session:
        query = """
        MATCH (m:Message)
        WHERE toLower(m.text) CONTAINS toLower($query)
        RETURN m
        LIMIT $limit
        """
        result = session.run(query, query=query_text, limit=limit)
        messages = []
        for record in result:
            message = dict(record["m"])
            messages.append(message)
        return messages 