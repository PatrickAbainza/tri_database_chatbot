import pytest
import httpx
import asyncio
from typing import Dict, List, Any

pytestmark = pytest.mark.asyncio

SERVICES = {
    "chatbot": "http://localhost:8000",
    "mcp": "http://localhost:8001",
    "neo4j": "http://localhost:8002",
    "weaviate": "http://localhost:8003",
    "relational": "http://localhost:8004"
}

async def check_service_health(client: httpx.AsyncClient, service_url: str) -> bool:
    """Check if a service is healthy."""
    try:
        response = await client.get(f"{service_url}/health")
        return response.status_code == 200
    except httpx.RequestError:
        return False

async def get_service_status(client: httpx.AsyncClient) -> Dict[str, bool]:
    """Get health status for all services."""
    status = {}
    for name, url in SERVICES.items():
        status[name] = await check_service_health(client, url)
    return status

class TestSystem:
    """System-level integration tests."""

    async def test_system_initialization(self, http_client: httpx.AsyncClient):
        """Test that all services initialize and become healthy."""
        status = await get_service_status(http_client)
        
        assert all(status.values()), \
            f"Not all services are healthy. Status: {status}"

    async def test_service_discovery(self, http_client: httpx.AsyncClient):
        """Test that services can discover and communicate with each other."""
        # Test chatbot -> MCP discovery
        response = await http_client.post(
            f"{SERVICES['chatbot']}/chat",
            json={"user_input": "Test message"}
        )
        assert response.status_code == 200
        
        # Test MCP -> Database discovery
        test_queries = [
            "Find connections in graph",  # Should route to Neo4j
            "Search similar vectors",     # Should route to Weaviate
            "Get user data"              # Should route to Relational
        ]
        
        for query in test_queries:
            response = await http_client.post(
                f"{SERVICES['chatbot']}/chat",
                json={"user_input": query}
            )
            assert response.status_code == 200
            assert "error" not in response.json()

    async def test_error_recovery(self, http_client: httpx.AsyncClient):
        """Test system's ability to recover from errors."""
        # Test system handling of malformed requests
        test_cases = [
            # Missing message field
            {
                "url": f"{SERVICES['chatbot']}/chat",
                "payload": {},
                "expected_status": 422
            },
            # Empty message
            {
                "url": f"{SERVICES['chatbot']}/chat",
                "payload": {"user_input": ""},
                "expected_status": 422
            },
            # Invalid route
            {
                "url": f"{SERVICES['mcp']}/invalid",
                "payload": {},
                "expected_status": 404
            }
        ]
        
        for test_case in test_cases:
            response = await http_client.post(
                test_case["url"],
                json=test_case["payload"]
            )
            assert response.status_code == test_case["expected_status"]
            
            # Verify system remains operational after error
            status = await get_service_status(http_client)
            assert all(status.values()), \
                "System health compromised after error"

    async def test_concurrent_requests(self, http_client: httpx.AsyncClient):
        """Test system's ability to handle concurrent requests."""
        async def make_request(message: str) -> Dict[str, Any]:
            response = await http_client.post(
                f"{SERVICES['chatbot']}/chat",
                json={"user_input": message}
            )
            return response.json()
        
        # Create multiple concurrent requests
        messages = [
            "Query graph database",
            "Search vector database",
            "Get user profile",
            "Find connections",
            "Search similar documents"
        ]
        
        tasks = [make_request(msg) for msg in messages]
        responses = await asyncio.gather(*tasks)
        
        # Verify all requests succeeded
        assert len(responses) == len(messages)
        for response in responses:
            assert "error" not in response

    async def test_system_resilience(self, http_client: httpx.AsyncClient):
        """Test system's resilience to various scenarios."""
        # Test handling of rapid sequential requests
        for _ in range(5):
            response = await http_client.post(
                f"{SERVICES['chatbot']}/chat",
                json={"user_input": "Test message"}
            )
            assert response.status_code == 200
            
            # No delay between requests to stress test
            
        # Verify system health after stress
        status = await get_service_status(http_client)
        assert all(status.values()), \
            "System health compromised after stress test"