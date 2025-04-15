from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import httpx
from typing import Optional, Dict, Any, Union
from enum import Enum

app = FastAPI(title="Chatbot Service")

# Constants
MCP_SERVICE_URL = "http://mcp_service:8001"

class DatabaseType(str, Enum):
    NEO4J = "neo4j"
    WEAVIATE = "weaviate"
    RELATIONAL = "relational"

class ChatRequest(BaseModel):
    # Add validation: non-empty string with max length of 4000 chars
    user_input: constr(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    # Support different response types based on database
    response: str
    graph: Optional[Dict[str, Any]] = None  # For Neo4j responses
    nodes: Optional[list] = None  # For Neo4j responses
    relationships: Optional[list] = None  # For Neo4j responses
    similar_docs: Optional[list] = None  # For Weaviate responses
    results: Optional[list] = None  # For Weaviate responses
    data: Optional[Dict[str, Any]] = None  # For Relational responses
    records: Optional[list] = None  # For Relational responses

def detect_intent(user_input: str) -> str:
    """
    Detect intent from user input to determine appropriate database routing.
    """
    user_input = user_input.lower()
    
    # Graph relationship queries
    if any(term in user_input for term in ["connection", "relationship", "link", "between"]):
        return "graph_relationships"
    
    # Semantic search queries
    if any(term in user_input for term in ["similar", "find", "search", "like"]):
        return "semantic_search"
    
    # Structured data queries
    if any(term in user_input for term in ["profile", "user", "data", "record", "transaction"]):
        return "structured_data"
    
    # Default to graph relationships
    return "graph_relationships"

async def route_to_mcp(query: str, intent: str) -> Dict[str, Any]:
    """
    Route request to MCP service and get appropriate database response.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{MCP_SERVICE_URL}/route",
                json={"query": query, "intent": intent},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"MCP service error: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat request and return a response from appropriate database.
    
    Parameters:
        request (ChatRequest): Chat request with user input
            - user_input must not be empty
            - user_input must not exceed 4000 characters
    
    Returns:
        ChatResponse: Response with appropriate fields based on database type
    """
    # Detect intent from user input
    intent = detect_intent(request.user_input)
    
    # Route request to MCP service
    mcp_response = await route_to_mcp(request.user_input, intent)
    
    # Initialize response with base fields
    response_data = {"response": mcp_response.get("response", "")}
    
    # Add database-specific fields based on routing
    database = mcp_response.get("database")
    if database == DatabaseType.NEO4J:
        response_data.update({
            "graph": {"nodes": [], "relationships": []},  # Mock graph data
            "nodes": [],
            "relationships": []
        })
    elif database == DatabaseType.WEAVIATE:
        response_data.update({
            "similar_docs": [],  # Mock similar docs
            "results": []
        })
    elif database == DatabaseType.RELATIONAL:
        response_data.update({
            "data": {},  # Mock data
            "records": []
        })
    
    return ChatResponse(**response_data)

@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint that returns OK status.
    """
    return {"status": "ok"}
