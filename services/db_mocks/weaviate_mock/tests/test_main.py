from fastapi.testclient import TestClient
import pytest
import numpy as np
import asyncio
import concurrent.futures
from src.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint functionality for weaviate mock service.

    Purpose:
        Verify that the /health endpoint returns correct status and service information.
    
    Test Scenario:
        Send GET request to /health endpoint
    
    Expected Outcome:
        - Status code should be 200
        - Response JSON should contain:
            - status: "healthy"
            - service: "weaviate-mock"
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "weaviate-mock"

def test_vector_search():
    """Test vector search functionality with complete parameters.

    Purpose:
        Verify that the /query endpoint correctly processes vector similarity
        search requests with all optional parameters specified.
    
    Test Scenario:
        Send POST request with vector query and all parameters
        
    Input:
        JSON payload with:
        - vector: 128-dimensional random vector
        - class_name: "Document"
        - limit: 2
        - distance_threshold: 1.0
    
    Expected Outcome:
        - Status code should be 200
        - Response should include results array where each result:
            - Has valid id (string)
            - Matches requested class_name
            - Has distance within threshold
            - Contains properties dictionary
            - Results count <= specified limit
    """
    # Create a mock query vector
    query_vector = np.random.rand(128).tolist()
    
    request_data = {
        "vector": query_vector,
        "class_name": "Document",
        "limit": 2,
        "distance_threshold": 1.0
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "results" in data
    results = data["results"]
    
    # Check if results are limited correctly
    assert len(results) <= request_data["limit"]
    
    # Verify result structure
    for result in results:
        assert "id" in result
        assert "class_name" in result
        assert "distance" in result
        assert "properties" in result
        
        # Verify result values
        assert isinstance(result["id"], str)
        assert result["class_name"] == "Document"
        assert isinstance(result["distance"], float)
        assert result["distance"] <= request_data["distance_threshold"]
        assert isinstance(result["properties"], dict)

def test_vector_search_with_defaults():
    """Test vector search functionality with minimal required parameters.

    Purpose:
        Verify that the /query endpoint works correctly with only
        required parameters, using default values for optional fields.
    
    Test Scenario:
        Send POST request with only vector and class_name
        
    Input:
        JSON payload with:
        - vector: 128-dimensional random vector
        - class_name: "Document"
    
    Expected Outcome:
        - Status code should be 200
        - Response should include results array
    """
    query_vector = np.random.rand(128).tolist()
    
    # Only provide required fields
    request_data = {
        "vector": query_vector,
        "class_name": "Document"
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data

def test_invalid_vector_query():
    """Test vector search with invalid inputs.

    Purpose:
        Verify that the /query endpoint properly handles invalid requests
        and incorrect vector dimensions.
    
    Test Scenario:
        1. Send POST request with empty payload
        2. Send POST request with incorrect vector dimension
        
    Input:
        1. Empty JSON payload {}
        2. JSON payload with 2D vector instead of 128D
    
    Expected Outcome:
        1. Status code 422 for missing required fields
        2. Status code 422 with message about vector dimension
    """
    # Missing required fields
    response = client.post("/query", json={})
    assert response.status_code == 422  # Validation error
    
    # Invalid vector dimension
    request_data = {
        "vector": [1.0, 2.0],  # Wrong dimension (should be 128)
        "class_name": "Document"
    }
    response = client.post("/query", json=request_data)
    assert response.status_code == 422  # Should fail with validation error
    error_detail = response.json()["detail"]
    assert "Vector dimension must be 128" in error_detail[0]["msg"]

def test_nonexistent_class():
    """Test vector search with non-existent class name.

    Purpose:
        Verify that the /query endpoint handles requests for
        non-existent classes gracefully.
    
    Test Scenario:
        Send POST request with valid vector but non-existent class
        
    Input:
        JSON payload with:
        - vector: 128-dimensional random vector
        - class_name: "NonexistentClass"
    
    Expected Outcome:
        - Status code should be 200
        - Response should include empty results array
    """
    query_vector = np.random.rand(128).tolist()
    
    request_data = {
        "vector": query_vector,
        "class_name": "NonexistentClass"
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0  # Should return empty results

def test_filter_combinations():
    """Test vector search with complex filter combinations.

    Purpose:
        Verify that the /query endpoint correctly handles searches combining
        vector similarity with specific property filters.
    
    Test Scenario:
        Send multiple POST requests with different filter combinations
        
    Input:
        Multiple queries filtering by vector similarity and document properties
    
    Expected Outcome:
        - Status code should be 200
        - Results should match both vector similarity and property criteria
        - Results should be properly ordered by distance
    """
    query_vector = np.random.rand(128).tolist()
    
    # Test combining distance threshold with category filter
    request_data = {
        "vector": query_vector,
        "class_name": "Document",
        "distance_threshold": 0.5
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # Verify filtered results
    for result in data["results"]:
        assert result["distance"] <= 0.5
        assert "technology" in result["properties"]["category"] or "research" in result["properties"]["category"]

    # Test with strict limit and category
    request_data = {
        "vector": query_vector,
        "class_name": "Document",
        "limit": 1,
        "distance_threshold": 1.0
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 1

def test_concurrent_load():
    """Test vector search performance under concurrent load.

    Purpose:
        Verify that the /query endpoint handles multiple concurrent
        requests efficiently and maintains consistency.
    
    Test Scenario:
        Send multiple concurrent vector search requests
        
    Input:
        Multiple concurrent requests with different vectors
    
    Expected Outcome:
        - All requests should complete successfully
        - Response structure should remain consistent
        - No errors under concurrent load
    """
    def make_request():
        query_vector = np.random.rand(128).tolist()
        request_data = {
            "vector": query_vector,
            "class_name": "Document",
            "limit": 2
        }
        response = client.post("/query", json=request_data)
        return response.status_code, response.json()
    
    # Test with 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [future.result() for future in futures]
    
    # Verify all requests succeeded
    for status_code, response_data in results:
        assert status_code == 200
        assert "results" in response_data
        
        # Verify response structure maintained under load
        for result in response_data["results"]:
            assert "id" in result
            assert "class_name" in result
            assert "distance" in result
            assert "properties" in result

def test_malformed_vectors():
    """Test handling of malformed vector inputs.

    Purpose:
        Verify that the /query endpoint properly handles and validates
        various types of malformed vector inputs.
    
    Test Scenario:
        Send requests with different types of malformed vectors
        
    Input:
        Various malformed vector inputs
    
    Expected Outcome:
        - Should properly validate and reject malformed inputs
        - Should return appropriate error messages
        - Should maintain service stability
    """
    test_cases = [
        # Empty vector
        {
            "vector": [],
            "class_name": "Document"
        },
        # Vector with non-numeric values
        {
            "vector": ["not", "a", "vector"] + [0.0] * 125,
            "class_name": "Document"
        },
        # Vector with None values
        {
            "vector": [None] * 128,
            "class_name": "Document"
        },
        # Vector with invalid numeric values
        {
            "vector": ["inf"] * 128,
            "class_name": "Document"
        }
    ]
    
    for test_case in test_cases:
        response = client.post("/query", json=test_case)
        assert response.status_code == 422  # Should be validation error
        
        error_detail = response.json()["detail"]
        assert isinstance(error_detail, list)  # Pydantic returns an array of errors
        assert len(error_detail) > 0  # Should have at least one error
        assert "msg" in error_detail[0]  # Each error should have a message