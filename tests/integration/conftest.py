import asyncio
import httpx
import pytest
from typing import AsyncGenerator
import pytest_asyncio

SERVICE_URLS = {
    "chatbot": "http://localhost:8000",
    "mcp": "http://localhost:8001",
    "neo4j": "http://localhost:8002",
    "weaviate": "http://localhost:8003",
    "relational": "http://localhost:8004"
}

async def is_service_ready(client: httpx.AsyncClient, url: str, retries: int = 10, delay: int = 3) -> bool:
    """Check if a service is ready by polling its health endpoint."""
    for _ in range(retries):
        try:
            response = await client.get(f"{url}/health", timeout=5.0)
            if response.status_code == 200:
                return True
        except httpx.RequestError:
            pass
        await asyncio.sleep(delay)
    return False

@pytest_asyncio.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create a shared HTTP client for the test session."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def ensure_services(http_client: httpx.AsyncClient):
    """Ensure all services are running before starting tests."""
    print("\nWaiting for services to be ready...")
    services_status = []
    
    for service_name, url in SERVICE_URLS.items():
        print(f"Checking {service_name}...")
        is_ready = await is_service_ready(http_client, url)
        services_status.append((service_name, is_ready))
        print(f"{service_name}: {'ready' if is_ready else 'not ready'}")
    
    failed_services = [name for name, status in services_status if not status]
    
    if failed_services:
        pytest.fail(f"Services not ready: {', '.join(failed_services)}. "
                   f"Ensure docker-compose is running.")

class TestContext:
    """Helper class to store shared test context."""
    def __init__(self):
        self.created_data = []
        self.cleanup_tasks = []

@pytest.fixture
def test_context():
    """Provide a fresh test context for each test."""
    return TestContext()