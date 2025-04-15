from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async client fixture for testing asynchronous endpoints.

    Creates an AsyncClient instance for making async HTTP requests during tests.
    Uses base_url to connect to test server.

    Yields:
        AsyncClient: Configured async client for testing
    """
    async with AsyncClient(base_url="http://test") as ac:
        yield ac


def test_health_check(client: TestClient) -> None:
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


def test_health_check_response_time(client: TestClient) -> None:
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


@pytest.mark.asyncio
async def test_chat_endpoint(async_client: AsyncClient, client: TestClient) -> None:
    """Test the chat endpoint with valid input.

    Purpose:
        Verify that the /chat endpoint handles valid messages correctly.
    
    Test Scenario:
        Send POST request to /chat with valid message format
        
    Input:
        JSON payload with "user_input" field containing "Hello"
    
    Expected Outcome:
        - Status code should be 200
        - Response should contain stubbed MCP interaction message
        - Response should match ChatResponse schema
    """
    test_message = {"user_input": "Hello"}
    # Use the test client to make synchronous request
    response = client.post("/chat", json=test_message)

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert data == {"response": "Acknowledged. MCP interaction stubbed."}


@pytest.mark.asyncio
async def test_chat_endpoint_empty_input(async_client: AsyncClient, client: TestClient) -> None:
    """Test the chat endpoint with empty user input.

    Purpose:
        Verify that the /chat endpoint properly handles empty input strings.
    
    Test Scenario:
        Send POST request to /chat with empty string as user_input
        
    Input:
        JSON payload with "user_input": ""
    
    Expected Outcome:
        - Status code should be 422 (Unprocessable Entity)
        - Response should indicate validation error
    """
    test_message = {"user_input": ""}
    response = client.post("/chat", json=test_message)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_endpoint_oversized_input(async_client: AsyncClient, client: TestClient) -> None:
    """Test the chat endpoint with oversized input.

    Purpose:
        Verify that the /chat endpoint properly handles inputs exceeding size limits.
    
    Test Scenario:
        Send POST request to /chat with very large input string
        
    Input:
        JSON payload with "user_input" containing 5000 characters
    
    Expected Outcome:
        - Status code should be 422 (Unprocessable Entity)
        - Response should indicate input size validation error
    """
    oversized_input = "x" * 5000  # Create a 5000 character string
    test_message = {"user_input": oversized_input}
    response = client.post("/chat", json=test_message)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_endpoint_invalid_input(async_client: AsyncClient, client: TestClient) -> None:
    """Test the chat endpoint with invalid input format.

    Purpose:
        Verify that the /chat endpoint properly validates request payload.
    
    Test Scenario:
        Send POST request to /chat with invalid message format
        
    Input:
        JSON payload with incorrect field "invalid_key" instead of "user_input"
    
    Expected Outcome:
        - Status code should be 422 (Unprocessable Entity)
        - Response should indicate validation error
    """
    test_message = {"invalid_key": "Hello"}
    response = client.post("/chat", json=test_message)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_chat_endpoint_malformed_json(async_client: AsyncClient, client: TestClient) -> None:
    """Test the chat endpoint with malformed JSON.

    Purpose:
        Verify that the /chat endpoint properly handles malformed JSON requests.
    
    Test Scenario:
        Send POST request to /chat with invalid JSON data
        
    Input:
        Malformed JSON string
    
    Expected Outcome:
        - Status code should be 422 (Unprocessable Entity)
        - Response should indicate JSON parsing error
    """
    response = client.post(
        "/chat",
        content="{invalid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
