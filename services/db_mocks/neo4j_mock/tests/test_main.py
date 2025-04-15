from fastapi.testclient import TestClient
import pytest
from src.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint functionality for neo4j mock service.

    Purpose:
        Verify that the /health endpoint returns correct status and service information.
    
    Test Scenario:
        Send GET request to /health endpoint
    
    Expected Outcome:
        - Status code should be 200
        - Response JSON should contain:
            - status: "healthy"
            - service: "neo4j-mock"
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "neo4j-mock"

def test_query_endpoint():
    """Test the query endpoint with valid Cypher query and parameters.

    Purpose:
        Verify that the /query endpoint correctly processes Neo4j queries
        and returns properly structured graph data.
    
    Test Scenario:
        Send POST request with valid Cypher query and parameters
        
    Input:
        JSON payload with:
        - query: "MATCH (n:Person) RETURN n"
        - parameters: {"name": "John"}
    
    Expected Outcome:
        - Status code should be 200
        - Response should include:
            - nodes array with valid structure (id, labels, properties)
            - relationships array with valid structure
              (id, type, startNode, endNode, properties)
    """
    request_data = {
        "query": "MATCH (n:Person) RETURN n",
        "parameters": {"name": "John"}
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "nodes" in data
    assert "relationships" in data
    
    # Verify nodes content
    assert len(data["nodes"]) > 0
    for node in data["nodes"]:
        assert "id" in node
        assert "labels" in node
        assert "properties" in node
    
    # Verify relationships content
    assert len(data["relationships"]) > 0
    for rel in data["relationships"]:
        assert "id" in rel
        assert "type" in rel
        assert "startNode" in rel
        assert "endNode" in rel
        assert "properties" in rel

def test_query_endpoint_without_parameters():
    """Test the query endpoint with valid Cypher query but no parameters.

    Purpose:
        Verify that the /query endpoint handles queries without parameters correctly.
    
    Test Scenario:
        Send POST request with only Cypher query
        
    Input:
        JSON payload with:
        - query: "MATCH (n:Person) RETURN n"
        - no parameters field
    
    Expected Outcome:
        - Status code should be 200
        - Response should include basic nodes and relationships arrays
    """
    request_data = {
        "query": "MATCH (n:Person) RETURN n"
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "relationships" in data

def test_invalid_query_request():
    """Test the query endpoint with invalid request format.

    Purpose:
        Verify that the /query endpoint properly validates request payload
        and rejects empty requests.
    
    Test Scenario:
        Send POST request with empty JSON payload
        
    Input:
        Empty JSON payload {}
    
    Expected Outcome:
        - Status code should be 422 (Unprocessable Entity)
        - Response should indicate validation error
    """
    response = client.post("/query", json={})
    assert response.status_code == 422  # Validation error

def test_complex_graph_pattern():
    """Test the query endpoint with complex multi-hop graph pattern.

    Purpose:
        Verify that the /query endpoint correctly handles complex graph patterns
        involving multiple nodes and relationships.
    
    Test Scenario:
        Send POST request with a complex pattern matching query that traverses
        multiple relationships
        
    Input:
        JSON payload with query traversing from Person through multiple relationships
    
    Expected Outcome:
        - Status code should be 200
        - Response should include all nodes in the path
        - Relationships should show proper connectivity
    """
    request_data = {
        "query": """
        MATCH (p1:Person)-[:KNOWS]->(p2:Person)-[:WORKS_AT]->(c:Company)
        RETURN p1, p2, c
        """,
        "parameters": {}
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # Verify we have all expected node types
    node_labels = set()
    for node in data["nodes"]:
        node_labels.update(node["labels"])
    
    assert "Person" in node_labels
    assert "Company" in node_labels
    
    # Verify relationship chain
    rel_types = set(rel["type"] for rel in data["relationships"])
    assert "KNOWS" in rel_types
    assert "WORKS_AT" in rel_types

def test_parameter_binding():
    """Test parameter binding in Cypher queries.

    Purpose:
        Verify that the /query endpoint correctly handles parameter binding
        in Cypher queries.
    
    Test Scenario:
        Send POST request with a parameterized query using different parameter types
        
    Input:
        JSON payload with parameterized query and multiple parameter types
    
    Expected Outcome:
        - Status code should be 200
        - Parameters should be properly bound
        - Response should reflect parameter values
    """
    request_data = {
        "query": """
        MATCH (p:Person)
        WHERE p.name = $name AND p.age > $min_age
        RETURN p
        """,
        "parameters": {
            "name": "John",
            "min_age": 25
        }
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # Verify parameter usage
    matching_nodes = [
        node for node in data["nodes"]
        if node["properties"]["name"] == "John" 
        and node["properties"]["age"] > 25
    ]
    assert len(matching_nodes) > 0

def test_transaction_simulation():
    """Test simulated transaction handling.

    Purpose:
        Verify that the /query endpoint properly handles transaction-like
        operations maintaining data consistency.
    
    Test Scenario:
        Send series of queries that should be treated as a transaction
        
    Input:
        Multiple query requests that modify and then verify data state
    
    Expected Outcome:
        - Status code should be 200
        - Data modifications should be consistent
        - Related nodes and relationships should maintain integrity
    """
    # Create new node
    create_query = {
        "query": """
        CREATE (p:Person {name: 'Alice', age: 25})
        RETURN p
        """,
        "parameters": {}
    }
    
    response = client.post("/query", json=create_query)
    assert response.status_code == 200
    
    # Verify node creation
    verify_query = {
        "query": """
        MATCH (p:Person {name: 'Alice'})
        RETURN p
        """,
        "parameters": {}
    }
    
    response = client.post("/query", json=verify_query)
    assert response.status_code == 200
    data = response.json()
    
    new_nodes = [
        node for node in data["nodes"]
        if node["properties"].get("name") == "Alice"
    ]
    assert len(new_nodes) > 0
    assert new_nodes[0]["properties"]["age"] == 25

def test_invalid_parameter_type():
    """Test handling of invalid parameter types.

    Purpose:
        Verify that the /query endpoint properly validates parameter types
        and handles invalid parameter values appropriately.
    
    Test Scenario:
        Send query with invalid parameter types
        
    Input:
        Query with incorrect parameter type (string where number expected)
    
    Expected Outcome:
        - Should handle type mismatch gracefully
        - Should return appropriate error response
    """
    request_data = {
        "query": """
        MATCH (p:Person)
        WHERE p.age > $age
        RETURN p
        """,
        "parameters": {
            "age": "not_a_number"  # Invalid type for age comparison
        }
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code in [400, 422]  # Either bad request or validation error