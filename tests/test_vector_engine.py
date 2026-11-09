"""
Unit tests for VectorGuard Atlas Vector Search & Policy Drift Radar.
"""

import pytest
from vectorguard.models.policy import ContractAuditRequest, PolicyClause
from vectorguard.engine.vector_store import (
    AtlasVectorIndex,
    generate_semantic_embedding,
    cosine_similarity,
)
from vectorguard.engine.radar_agent import VectorGuardRadarAgent


@pytest.fixture
def compliant_contract():
    return ContractAuditRequest(
        contract_id="TEST-COMP-01",
        title="Compliant Cloud DPA",
        counterparty="Safe SaaS Corp",
        clauses=[
            PolicyClause(
                clause_id="C1",
                section_title="Instructions",
                text="The processor shall only process personal data on documented instructions from controller.",
                category="PRIVACY",
            ),
            PolicyClause(
                clause_id="C2",
                section_title="Notification",
                text="Processor shall notify controller of personal data breach within 72 hours.",
                category="COMPLIANCE",
            ),
        ],
    )


@pytest.fixture
def non_compliant_contract():
    return ContractAuditRequest(
        contract_id="TEST-FAIL-01",
        title="Predatory Vendor MSA",
        counterparty="Hostile Cloud Ltd",
        clauses=[
            PolicyClause(
                clause_id="TRAP-1",
                section_title="Data Exfiltration",
                text="Vendor reserves unilateral retention of customer personal data after termination without restriction.",
                category="PRIVACY",
            ),
            PolicyClause(
                clause_id="TRAP-2",
                section_title="Negligence Transfer",
                text="Customer shall indemnify vendor for vendor negligence during platform operations.",
                category="INDEMNITY",
            ),
        ],
    )


def test_semantic_embedding_generation():
    v1 = generate_semantic_embedding("processor shall only process personal data on documented instructions")
    v2 = generate_semantic_embedding("processor shall only process personal data on documented instructions")
    assert len(v1) == 64
    assert v1 == v2  # Deterministic unit vector
    assert pytest.approx(cosine_similarity(v1, v2), 0.001) == 1.0


def test_atlas_vector_index_search():
    index = AtlasVectorIndex()
    query = "immediate breach notification within 72 hours"
    results = index.search_nearest_mandate(query, k=1)
    assert len(results) == 1
    best_mandate, score = results[0]
    assert score > 0.0
    assert "GDPR" in best_mandate["mandate"] or "mandate" in best_mandate


@pytest.mark.asyncio
async def test_compliant_contract_audit(compliant_contract):
    agent = VectorGuardRadarAgent()
    result = await agent.audit_contract(compliant_contract)
    assert result.status == "COMPLIANT"
    assert result.compliance_score >= 85.0
    assert len(result.violations) == 0


@pytest.mark.asyncio
async def test_predatory_contract_triggers_rejection(non_compliant_contract):
    agent = VectorGuardRadarAgent()
    result = await agent.audit_contract(non_compliant_contract)
    assert result.status == "REJECTED"
    assert result.compliance_score < 50.0
    severities = [v.severity for v in result.violations]
    assert "CRITICAL" in severities
