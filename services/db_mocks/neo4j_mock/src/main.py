from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import networkx as nx

app = FastAPI(title="Neo4j Mock Service")

# Create a sample graph for mock responses
mock_graph = nx.DiGraph()
mock_graph.add_nodes_from([
    (1, {"labels": ["Person"], "properties": {"name": "John", "age": 30}}),
    (2, {"labels": ["Person"], "properties": {"name": "Jane", "age": 28}}),
    (3, {"labels": ["Company"], "properties": {"name": "TechCorp", "founded": 2020}})
])
mock_graph.add_edges_from([
    (1, 2, {"type": "KNOWS", "properties": {"since": 2019}}),
    (1, 3, {"type": "WORKS_AT", "properties": {"role": "Developer"}})
])

class QueryRequest(BaseModel):
    query: str
    parameters: Optional[Dict[str, Any]] = None

class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "neo4j-mock"}

def validate_parameters(parameters: Dict[str, Any]):
    """Validate parameter types against graph schema"""
    if not parameters:
        return
        
    # Check type compatibility with existing node properties
    for node_id, data in mock_graph.nodes(data=True):
        props = data.get("properties", {})
        for key, value in props.items():
            if key in parameters:
                param_value = parameters[key]
                if not isinstance(param_value, type(value)):
                    raise HTTPException(
                        status_code=422,
                        detail=f"Parameter '{key}' type mismatch. Expected {type(value)}, got {type(param_value)}"
                    )

@app.post("/query", response_model=GraphResponse)
async def execute_query(request: QueryRequest):
    """Mock endpoint for executing Cypher-like queries"""
    
    # Validate parameters if provided
    if request.parameters:
        validate_parameters(request.parameters)
    
    # Handle CREATE operations
    if "CREATE" in request.query.upper():
        # Extract node properties from query (simple parsing)
        import re
        props_match = re.search(r'{(.*?)}', request.query)
        if props_match:
            props_str = props_match.group(1)
            props = {}
            for pair in props_str.split(','):
                key, value = pair.strip().split(':')
                key = key.strip()
                value = value.strip(' \'\"')
                # Convert value to appropriate type
                if value.isdigit():
                    value = int(value)
                props[key] = value
            
            # Add new node
            new_id = max(mock_graph.nodes()) + 1
            mock_graph.add_node(new_id, labels=["Person"], properties=props)
    
    # Return current graph state
    nodes = [
        {
            "id": node_id,
            "labels": data["labels"],
            "properties": data["properties"]
        }
        for node_id, data in mock_graph.nodes(data=True)
    ]
    
    relationships = [
        {
            "id": idx,
            "type": data["type"],
            "startNode": source,
            "endNode": target,
            "properties": data["properties"]
        }
        for idx, (source, target, data) in enumerate(mock_graph.edges(data=True))
    ]
    
    return GraphResponse(nodes=nodes, relationships=relationships)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)