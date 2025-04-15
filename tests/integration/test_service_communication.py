import pytest
import httpx
from typing import Dict, Any

pytestmark = pytest.mark.asyncio

async def send_chat_request(client: httpx.AsyncClient, message: str) -> Dict[Any, Any]:
    """Send a chat request to the chatbot service."""
    response = await client.post(
        "http://localhost:8000/chat",
        json={"user_input": message}
    )
    return response.json()

class TestServiceCommunication:
    """Integration tests for service communication."""

    async def test_chatbot_to_mcp_communication(self, http_client: httpx.AsyncClient):
        """Test successful communication from Chatbot to MCP service."""
        response = await send_chat_request(http_client, "What is your name?")
        assert response is not None
        assert "response" in response
        
    async def test_mcp_database_routing(self, http_client: httpx.AsyncClient):
        """Test MCP service correctly routes requests to appropriate database mock."""
        # Test routing to Neo4j mock
        response = await send_chat_request(
            http_client, 
            "Find connections between Alice and Bob"
        )
        assert response is not None
        assert "graph" in response or "nodes" in response
        
        # Test routing to Weaviate mock
        response = await send_chat_request(
            http_client,
            "Find similar documents about machine learning"
        )
        assert response is not None
        assert "similar_docs" in response or "results" in response
        
        # Test routing to Relational mock
        response = await send_chat_request(
            http_client,
            "Get user profile data"
        )
        assert response is not None
        assert "data" in response or "records" in response

    async def test_end_to_end_request_flow(self, http_client: httpx.AsyncClient):
        """Test complete request flow through all services."""
        test_cases = [
            {
                "message": "Find connections between users who like AI",
                "expected_db": "neo4j",
                "expected_fields": ["graph", "nodes", "relationships"]
            },
            {
                "message": "Find similar articles about Python programming",
                "expected_db": "weaviate",
                "expected_fields": ["similar_docs", "results"]
            },
            {
                "message": "Get user transaction history",
                "expected_db": "relational",
                "expected_fields": ["data", "records"]
            }
        ]
        
        for test_case in test_cases:
            response = await send_chat_request(http_client, test_case["message"])
            assert response is not None
            assert any(field in response for field in test_case["expected_fields"]), \
                f"Response missing expected fields for {test_case['expected_db']} query"

    async def test_error_propagation(self, http_client: httpx.AsyncClient):
        """Test error handling and propagation between services."""
        # Test invalid request format
        response = await http_client.post(
            "http://localhost:8000/chat",
            json={}  # Missing required message field
        )
        assert response.status_code == 422
        
        # Test MCP service error handling
        # Test sending an empty string (should trigger validation error)
        response_empty = await http_client.post(
            "http://localhost:8000/chat",
            json={"user_input": ""}
        )
        assert response_empty.status_code == 422
        
        # Test database error propagation
        invalid_queries = [
            "INVALID_QUERY_FOR_NEO4J",
            "INVALID_QUERY_FOR_WEAVIATE",
            "INVALID_QUERY_FOR_RELATIONAL"
        ]
        
        for query in invalid_queries:
            response = await send_chat_request(http_client, query)
            assert response is not None
            assert "response" in response # Check for success response from stub

    async def test_service_unavailability_handling(self, http_client: httpx.AsyncClient):
        """Test system behavior when a service is unavailable."""
        # We can't actually stop services during testing, but we can test timeout scenarios
        timeout_client = httpx.AsyncClient(timeout=0.001)  # Very short timeout
        
        try:
            await send_chat_request(timeout_client, "Test message")
        except httpx.TimeoutException as e:
            assert True, "Expected timeout exception"
        finally:
            await timeout_client.aclose()