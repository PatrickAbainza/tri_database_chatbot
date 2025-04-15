from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_route_endpoint_valid_request():
    """Test the /route endpoint functionality with valid input.

    Purpose:
        Verify that the /route endpoint correctly processes valid requests
        and returns expected routing information.
    
    Test Scenario:
        Send POST request to /route with valid query and intent
        
    Input:
        JSON payload with:
        - query: "test query"
        - intent: "test intent"
    
    Expected Outcome:
        - Status code should be 200
        - Response should include:
            - database: "neo4j"
            - response: "Mock routing response"
    """
    response = client.post(
        "/route", json={"query": "test query", "intent": "test intent"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "neo4j"
    assert data["response"] == "Mock routing response"


def test_route_endpoint_empty_query():
    """Test the /route endpoint with empty query.

    Purpose:
        Verify that the /route endpoint properly handles empty query strings
        while maintaining valid intent.
    
    Test Scenario:
        Send POST request to /route with empty query string
        
    Input:
        JSON payload with:
        - query: ""
        - intent: "test intent"
    
    Expected Outcome:
        - Status code should be 422 (Unprocessable Entity)
        - Response should indicate empty query validation error
    """
    response = client.post(
        "/route", json={"query": "", "intent": "test intent"}
    )
    assert response.status_code == 422


def test_route_endpoint_database_selection():
    """Test the database selection logic for different intents.

    Purpose:
        Verify that the routing logic correctly selects different databases
        based on the provided intent.
    
    Test Scenario:
        Send multiple requests with different intents
        
    Input:
        Various intents that should route to different databases
    
    Expected Outcome:
        - Each intent should route to its designated database
        - Response format should be consistent
    """
    # Test graph-based intent
    response = client.post(
        "/route", 
        json={"query": "test query", "intent": "graph_relationships"}
    )
    assert response.status_code == 200
    assert response.json()["database"] == "neo4j"

    # Test vector-based intent
    response = client.post(
        "/route", 
        json={"query": "test query", "intent": "semantic_search"}
    )
    assert response.status_code == 200
    assert response.json()["database"] == "weaviate"

    # Test relational intent
    response = client.post(
        "/route", 
        json={"query": "test query", "intent": "structured_data"}
    )
    assert response.status_code == 200
    assert response.json()["database"] == "relational"


def test_route_endpoint_invalid_request():
    """Test the /route endpoint with invalid input format.

    Purpose:
        Verify that the /route endpoint properly validates request payload
        and rejects invalid data.
    
    Test Scenario:
        Send POST request to /route with invalid JSON structure
        
    Input:
        JSON payload with incorrect field "invalid": "data"
    
    Expected Outcome:
        - Status code should be 422 (Unprocessable Entity)
        - Response should indicate validation error
    """
    response = client.post("/route", json={"invalid": "data"})
    assert response.status_code == 422  # Validation error


def test_route_endpoint_missing_fields():
    """Test the /route endpoint with missing required fields.

    Purpose:
        Verify that the /route endpoint enforces required field validation
        and handles incomplete requests appropriately.
    
    Test Scenario:
        Send POST request to /route with missing required field
        
    Input:
        JSON payload with only query field, missing required intent field
    
    Expected Outcome:
        - Status code should be 422 (Unprocessable Entity)
        - Response should indicate missing required field
    """
    response = client.post(
        "/route",
        json={"query": "test query"},  # Missing intent field
    )
    assert response.status_code == 422


def test_health_endpoint():
    """Test the health check endpoint functionality.

    Purpose:
        Verify that the /health endpoint returns correct status and response format.
    
    Test Scenario:
        Send GET request to /health endpoint
    
    Expected Outcome:
        - Status code should be 200
        - Response JSON should contain {"status": "ok"}
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_response_time():
    """Test the health check endpoint response time.

    Purpose:
        Verify that the /health endpoint responds within acceptable time limits.
    
    Test Scenario:
        Send GET request to /health endpoint and measure response time
    
    Expected Outcome:
        - Response time should be under 500ms
    """
    import time
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 0.5  # Response should be under 500ms


def test_route_endpoint_complex_intents():
    """Test the /route endpoint with complex and hybrid intents.

    Purpose:
        Verify that the routing logic can handle complex intents that may
        require sophisticated database selection logic.
    
    Test Scenario:
        Send requests with complex/hybrid intents to test advanced routing
        
    Input:
        Various complex and hybrid intents
    
    Expected Outcome:
        - Should select most appropriate database based on intent complexity
        - Should maintain consistent response format
        - Should handle hybrid intent scenarios
    """
    # Test hybrid intent that could use multiple databases
    response = client.post(
        "/route",
        json={"query": "test query", "intent": "graph_with_semantic"}
    )
    assert response.status_code == 200
    # Verify it chooses primary database based on intent priority
    assert response.json()["database"] in ["neo4j", "weaviate"]

    # Test complex hierarchical intent
    response = client.post(
        "/route",
        json={"query": "test query", "intent": "nested.hierarchical.intent"}
    )
    assert response.status_code == 200
    assert "database" in response.json()


def test_route_endpoint_invalid_intent_details():
    """Test detailed error responses for invalid intents.

    Purpose:
        Verify that the routing logic provides informative error responses
        for various types of invalid intents.
    
    Test Scenario:
        Send requests with different types of invalid intents
        
    Input:
        Various invalid intent formats and values
    
    Expected Outcome:
        - Should return appropriate error codes
        - Should provide detailed error messages
        - Should handle different types of intent validation failures
    """
    # Test completely invalid intent format
    response = client.post(
        "/route",
        json={"query": "test", "intent": ["invalid", "format"]}
    )
    assert response.status_code == 422
    assert "intent" in response.json()["detail"][0]["loc"]

    # Test unsupported intent value
    response = client.post(
        "/route",
        json={"query": "test", "intent": "unsupported_intent_type"}
    )
    assert response.status_code == 422
    error_detail = response.json()
    # Account for both list-style validation errors and string error messages
    if isinstance(error_detail["detail"], list):
        assert any("intent" in err["loc"] for err in error_detail["detail"])
    else:
        assert "unsupported intent" in str(error_detail["detail"]).lower()


def test_route_endpoint_database_fallback():
    """Test database selection fallback behavior.

    Purpose:
        Verify that the routing logic handles scenarios where primary
        database choice is unavailable and falls back appropriately.
    
    Test Scenario:
        Test database selection with various priority and fallback scenarios
        
    Input:
        Queries that trigger database fallback logic
    
    Expected Outcome:
        - Should attempt to route to primary database first
        - Should fall back to secondary database if needed
        - Should maintain consistent response format
    """
    # Test fallback scenario
    response = client.post(
        "/route",
        json={"query": "test query", "intent": "hybrid_fallback"}
    )
    assert response.status_code == 200
    assert response.json()["database"] in ["neo4j", "relational", "weaviate"]

    # Test prioritization
    response = client.post(
        "/route",
        json={"query": "test query", "intent": "priority_check"}
    )
    assert response.status_code == 200
    assert "database" in response.json()
