"""Database connection and session management for Neo4j."""

import os
from neo4j import GraphDatabase
from typing import Generator


class Neo4jConnection:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        return self.driver.session()


# Global database connection
_db_connection = None


def get_connection() -> Neo4jConnection:
    """Get or create database connection."""
    global _db_connection
    if _db_connection is None:
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "local_neo4j_pw")
        
        _db_connection = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
    
    return _db_connection


def get_session():
    """Get a new database session."""
    connection = get_connection()
    return connection.get_session()


def close_connection():
    """Close the database connection."""
    global _db_connection
    if _db_connection:
        _db_connection.close()
        _db_connection = None 