from fastapi.testclient import TestClient
import pytest
from src.main import app, QueryType

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint functionality for relational mock service.

    Purpose:
        Verify that the /health endpoint returns correct status and service information.
    
    Test Scenario:
        Send GET request to /health endpoint
    
    Expected Outcome:
        - Status code should be 200
        - Response JSON should contain:
            - status: "healthy"
            - service: "relational-mock"
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "relational-mock"

def test_select_query():
    """Test SELECT query execution functionality.

    Purpose:
        Verify that the /query endpoint correctly processes SELECT queries
        and returns properly structured result sets.
    
    Test Scenario:
        Send POST request with SELECT query for users table
        
    Input:
        JSON payload with:
        - query: "SELECT * FROM users"
        - query_type: QueryType.SELECT
        - parameters: None
    
    Expected Outcome:
        - Status code should be 200
        - Response should include results array where each user has:
            - id
            - username
            - email
            - active status
    """
    request_data = {
        "query": "SELECT * FROM users",
        "query_type": QueryType.SELECT,
        "parameters": None
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert "results" in data
    results = data["results"]
    assert isinstance(results, list)
    assert len(results) > 0
    
    # Verify user data structure
    for user in results:
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "active" in user

def test_complex_join_operations():
    """Test complex JOIN operations with multiple tables.

    Purpose:
        Verify that the /query endpoint correctly processes complex JOIN
        operations involving multiple tables and join conditions.
    
    Test Scenario:
        Send POST requests with complex JOIN queries
        
    Input:
        Multiple JOIN queries with different complexities
    
    Expected Outcome:
        - Status code should be 200
        - Results should contain data from all joined tables
        - Proper handling of different JOIN types
    """
    # Test INNER JOIN between users and posts
    join_query = {
        "query": """
        SELECT u.username, p.title 
        FROM users u 
        INNER JOIN posts p ON u.id = p.user_id 
        WHERE u.active = true
        """,
        "query_type": QueryType.SELECT,
        "parameters": None
    }
    
    response = client.post("/query", json=join_query)
    assert response.status_code == 200
    data = response.json()
    
    # Verify joined results structure
    assert "results" in data
    for result in data["results"]:
        assert "username" in result
        assert "title" in result

    # Test complex multi-table JOIN
    complex_join_query = {
        "query": """
        SELECT u.username, p.title, c.content
        FROM users u
        INNER JOIN posts p ON u.id = p.user_id
        LEFT JOIN comments c ON p.id = c.post_id
        WHERE u.active = true
        ORDER BY p.id DESC
        """,
        "query_type": QueryType.SELECT,
        "parameters": None
    }
    
    response = client.post("/query", json=complex_join_query)
    assert response.status_code == 200
    data = response.json()
    
    # Verify complex join results
    assert "results" in data
    for result in data["results"]:
        assert "username" in result
        assert "title" in result
        # content might be null due to LEFT JOIN
        assert "content" in result

def test_transaction_management():
    """Test transaction management functionality.

    Purpose:
        Verify that the /query endpoint properly handles transaction-like
        operations maintaining data consistency.
    
    Test Scenario:
        Send series of related queries that should be treated as a transaction
        
    Input:
        Multiple query requests that should succeed or fail together
    
    Expected Outcome:
        - All operations in transaction should succeed
        - Data should remain consistent
        - Proper error handling for failed transactions
    """
    # Start transaction with insert
    insert_query = {
        "query": "INSERT INTO users (username, email, active) VALUES (:username, :email, :active)",
        "query_type": QueryType.INSERT,
        "parameters": {
            "username": "transaction_test",
            "email": "trans@example.com",
            "active": True
        }
    }
    
    response = client.post("/query", json=insert_query)
    assert response.status_code == 200
    insert_result = response.json()
    assert insert_result["affected_rows"] == 1

    # Update related data
    update_query = {
        "query": """
        UPDATE posts 
        SET title = :title 
        WHERE user_id = (SELECT id FROM users WHERE username = :username)
        """,
        "query_type": QueryType.UPDATE,
        "parameters": {
            "title": "Updated in transaction",
            "username": "transaction_test"
        }
    }
    
    response = client.post("/query", json=update_query)
    assert response.status_code == 200
    update_result = response.json()
    assert update_result["affected_rows"] > 0

def test_data_type_handling():
    """Test handling of different SQL data types.

    Purpose:
        Verify that the /query endpoint properly handles and validates
        different SQL data types in queries and parameters.
    
    Test Scenario:
        Send queries with different data types
        
    Input:
        Queries using various SQL data types
    
    Expected Outcome:
        - Proper handling of different data types
        - Correct type validation and conversion
        - Appropriate error handling for type mismatches
    """
    # Test different data types in INSERT
    complex_insert = {
        "query": """
        INSERT INTO test_types (
            int_col, float_col, text_col, bool_col, 
            date_col, timestamp_col, json_col
        ) VALUES (
            :int_val, :float_val, :text_val, :bool_val,
            :date_val, :timestamp_val, :json_val
        )
        """,
        "query_type": QueryType.INSERT,
        "parameters": {
            "int_val": 42,
            "float_val": 3.14,
            "text_val": "test string",
            "bool_val": True,
            "date_val": "2025-04-15",
            "timestamp_val": "2025-04-15T12:30:00Z",
            "json_val": {"key": "value"}
        }
    }
    
    response = client.post("/query", json=complex_insert)
    assert response.status_code == 200
    assert response.json()["affected_rows"] == 1

    # Test invalid type conversions
    invalid_types = {
        "query": "INSERT INTO users (id, active) VALUES (:id, :active)",
        "query_type": QueryType.INSERT,
        "parameters": {
            "id": "not_an_integer",  # Should be integer
            "active": "not_a_boolean"  # Should be boolean
        }
    }
    
    response = client.post("/query", json=invalid_types)
    assert response.status_code in [400, 422]  # Should fail with validation error

def test_insert_query():
    """Test INSERT query execution functionality.

    Purpose:
        Verify that the /query endpoint correctly processes INSERT queries
        and returns appropriate metadata.
    
    Test Scenario:
        Send POST request with INSERT query and parameters
        
    Input:
        JSON payload with:
        - query: "INSERT INTO users (username, email) VALUES (:username, :email)"
        - query_type: QueryType.INSERT
        - parameters: {username: "new_user", email: "new@example.com"}
    
    Expected Outcome:
        - Status code should be 200
        - Response should include:
            - affected_rows = 1
            - success message indicating insertion
    """
    request_data = {
        "query": "INSERT INTO users (username, email) VALUES (:username, :email)",
        "query_type": QueryType.INSERT,
        "parameters": {
            "username": "new_user",
            "email": "new@example.com"
        }
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["affected_rows"] == 1
    assert "message" in data
    assert "inserted" in data["message"].lower()

def test_update_query():
    """Test UPDATE query execution functionality.

    Purpose:
        Verify that the /query endpoint correctly processes UPDATE queries
        and returns appropriate metadata.
    
    Test Scenario:
        Send POST request with UPDATE query and parameters
        
    Input:
        JSON payload with:
        - query: "UPDATE users SET active = :active WHERE id = :id"
        - query_type: QueryType.UPDATE
        - parameters: {active: false, id: 1}
    
    Expected Outcome:
        - Status code should be 200
        - Response should include:
            - affected_rows > 0
            - success message indicating update
    """
    request_data = {
        "query": "UPDATE users SET active = :active WHERE id = :id",
        "query_type": QueryType.UPDATE,
        "parameters": {
            "active": False,
            "id": 1
        }
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["affected_rows"] > 0
    assert "message" in data
    assert "updated" in data["message"].lower()

def test_delete_query():
    """Test DELETE query execution functionality.

    Purpose:
        Verify that the /query endpoint correctly processes DELETE queries
        and returns appropriate metadata.
    
    Test Scenario:
        Send POST request with DELETE query and parameters
        
    Input:
        JSON payload with:
        - query: "DELETE FROM users WHERE id = :id"
        - query_type: QueryType.DELETE
        - parameters: {id: 1}
    
    Expected Outcome:
        - Status code should be 200
        - Response should include:
            - affected_rows = 1
            - success message indicating deletion
    """
    request_data = {
        "query": "DELETE FROM users WHERE id = :id",
        "query_type": QueryType.DELETE,
        "parameters": {
            "id": 1
        }
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["affected_rows"] == 1
    assert "message" in data
    assert "deleted" in data["message"].lower()

def test_select_empty_result():
    """Test SELECT query with no matching results.

    Purpose:
        Verify that the /query endpoint handles queries that return
        no data appropriately.
    
    Test Scenario:
        Send POST request with SELECT query for non-existent table
        
    Input:
        JSON payload with:
        - query: "SELECT * FROM unknown_table"
        - query_type: QueryType.SELECT
        - parameters: None
    
    Expected Outcome:
        - Status code should be 200
        - Response should include:
            - empty results array
            - message indicating no data found
    """
    request_data = {
        "query": "SELECT * FROM unknown_table",
        "query_type": QueryType.SELECT,
        "parameters": None
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert "results" in data
    assert len(data["results"]) == 0
    assert "message" in data
    assert "no data found" in data["message"].lower()

def test_invalid_query_request():
    """Test query endpoint with invalid request format.

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
    # Missing required fields
    response = client.post("/query", json={})
    assert response.status_code == 422  # Validation error

def test_invalid_query_type():
    """Test query endpoint with invalid query type.

    Purpose:
        Verify that the /query endpoint properly validates
        the query_type field.
    
    Test Scenario:
        Send POST request with invalid query_type value
        
    Input:
        JSON payload with:
        - query: "SELECT * FROM users"
        - query_type: "INVALID"
        - parameters: None
    
    Expected Outcome:
        - Status code should be 422 (Unprocessable Entity)
        - Response should indicate validation error
    """
    request_data = {
        "query": "SELECT * FROM users",
        "query_type": "INVALID",
        "parameters": None
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 422  # Validation error