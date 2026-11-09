"""
API tests for VectorGuard.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from vectorguard.api.app import app


@pytest.mark.asyncio
async def test_vectorguard_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "MongoDB AI Innovators Challenge" in data["competition"]


@pytest.mark.asyncio
async def test_sample_contracts_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/sample/contracts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2


@pytest.mark.asyncio
async def test_audit_contract_endpoint():
    transport = ASGITransport(app=app)
    payload = {
        "contract_id": "CTR-TEST-99",
        "title": "Test MSA",
        "counterparty": "Test Corp",
        "contract_type": "DPA",
        "clauses": [
            {
                "clause_id": "C-1",
                "section_title": "Processing",
                "text": "Data is processed according to controller instructions.",
                "category": "PRIVACY",
            }
        ],
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/audit/contract", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["contract_id"] == "CTR-TEST-99"
        assert "compliance_score" in data
        assert "atlas_vector_metrics" in data
