from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, validator
from enum import Enum
from typing import Optional, List, Dict


app = FastAPI(
    title="MCP Service",
    description="Model Context Protocol Service - Central routing hub",
)


# Define supported intents and their database mappings
class DatabaseType(str, Enum):
    NEO4J = "neo4j"
    WEAVIATE = "weaviate"
    RELATIONAL = "relational"


# Database priority for hybrid intents
DATABASE_PRIORITIES = {
    "graph_with_semantic": [DatabaseType.NEO4J, DatabaseType.WEAVIATE],
    "hybrid_fallback": [DatabaseType.NEO4J, DatabaseType.RELATIONAL, DatabaseType.WEAVIATE],
    "priority_check": [DatabaseType.WEAVIATE, DatabaseType.NEO4J]
}

# Basic intent to database mapping
INTENT_TO_DB_MAP = {
    "graph_relationships": DatabaseType.NEO4J,
    "semantic_search": DatabaseType.WEAVIATE,
    "structured_data": DatabaseType.RELATIONAL,
    "test intent": DatabaseType.NEO4J
}

# Pydantic models for request/response validation
class RouteRequest(BaseModel):
    query: constr(min_length=1)
    intent: str

    @validator('intent')
    def validate_intent(cls, v):
        if not isinstance(v, str):
            raise ValueError("Intent must be a string")
        # Check if it's a known intent or a valid hierarchical intent
        if v not in INTENT_TO_DB_MAP and v not in DATABASE_PRIORITIES and not any(c for c in v if c == '.'):
            raise ValueError("Unsupported intent type")
        return v


class RouteResponse(BaseModel):
    database: str
    response: str
    fallback_info: Optional[Dict[str, str]] = None


class HealthResponse(BaseModel):
    status: str


def get_database_for_intent(intent: str) -> tuple[DatabaseType, Optional[Dict[str, str]]]:
    """
    Determine the appropriate database based on intent with fallback support.
    Returns tuple of (selected_database, fallback_info).
    """
    # Handle hierarchical intents
    if '.' in intent:
        # For demonstration, route hierarchical intents to Neo4j
        return DatabaseType.NEO4J, {"intent_type": "hierarchical"}

    # Check if it's a hybrid/complex intent with priorities
    if intent in DATABASE_PRIORITIES:
        fallback_info = {"primary_choice": DATABASE_PRIORITIES[intent][0]}
        
        # For demonstration, always use first available in priority list
        return DATABASE_PRIORITIES[intent][0], fallback_info

    # Fall back to basic intent mapping
    return INTENT_TO_DB_MAP.get(intent, DatabaseType.NEO4J), None


# API endpoints
@app.post("/route", response_model=RouteResponse)
async def route_request(request: RouteRequest) -> RouteResponse:
    """
    Route a request to the appropriate database mock based on query and intent.
    Handles complex routing scenarios including hybrid intents and fallbacks.
    """
    try:
        database, fallback_info = get_database_for_intent(request.intent)
        
        response = RouteResponse(
            database=database,
            response="Mock routing response",
            fallback_info=fallback_info
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify service status
    """
    return HealthResponse(status="ok")
