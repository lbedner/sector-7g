"""
Tests for worker API endpoints.

These tests focus on the worker HTTP endpoints that handle task enqueuing,
ensuring TaskRequest model works correctly with task_kwargs field and
validates the API contract.
"""

from collections.abc import AsyncIterator

from httpx import ASGITransport, AsyncClient
import pytest

from app.integrations.main import create_integrated_app


class TestWorkerEndpoints:
    """Test worker API endpoints for task enqueuing."""

    @pytest.fixture
    async def async_client(self) -> AsyncIterator[AsyncClient]:
        """Async HTTP client for testing.

        No auth or no DB in this stack, so no override needed — the
        endpoints are reachable without a bearer token.
        """
        app = create_integrated_app()

        # Manually trigger startup for health check registration
        from app.components.backend.hooks import backend_hooks

        await backend_hooks.discover_lifespan_hooks()
        await backend_hooks.execute_startup_hooks()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

        # Clean up after test: what the startup hooks began, stopped (left
        # running, the test's loop waits 300s for it as it closes).
        await backend_hooks.execute_shutdown_hooks()

    async def test_enqueue_task_invalid_queue_type(self, async_client, auth_headers):
        """Test error handling for invalid queue type."""
        task_request = {
            "task_name": "system_health_check",
            "queue_type": "invalid_queue",
            "args": [],
            "task_kwargs": {},
        }

        response = await async_client.post(
            "/api/v1/tasks/enqueue",
            json=task_request,
            headers=auth_headers,
        )

        # Should return 400 for invalid queue type
        assert response.status_code == 400
        response_data = response.json()
        assert "detail" in response_data
        assert response_data["detail"]["error"] == "invalid_queue_type"

    async def test_task_request_model_validation(self, async_client, auth_headers):
        """Test TaskRequest model validation."""
        # Missing required task_name field
        invalid_request = {"queue_type": "system", "args": [], "task_kwargs": {}}

        response = await async_client.post(
            "/api/v1/tasks/enqueue",
            json=invalid_request,
            headers=auth_headers,
        )

        # Should return 422 for validation error
        assert response.status_code == 422
