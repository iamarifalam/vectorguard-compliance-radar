"""
Pydantic Data Models for VectorGuard Compliance & Contract Policy Radar.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class PolicyClause(BaseModel):
    clause_id: str
    section_title: str
    text: str
    category: str = "COMPLIANCE"  # COMPLIANCE, LIABILITY, PRIVACY, INDEMNITY
    vector_embedding: Optional[List[float]] = None


class ContractAuditRequest(BaseModel):
    contract_id: str
    title: str
    counterparty: str
    contract_type: str = "VENDOR_MSA"  # VENDOR_MSA, DPA, EMPLOYMENT, TERMS_OF_SERVICE
    clauses: List[PolicyClause] = Field(default_factory=list)


class ComplianceViolation(BaseModel):
    violation_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    clause_id: str
    rule_breached: str
    matched_mandate: str  # e.g., "GDPR Art 28", "HIPAA §164.312", "SOC 2 Type II"
    similarity_score: float = Field(ge=0.0, le=1.0)
    risk_narrative: str
    remediation_clause: str


class ContractAuditResult(BaseModel):
    audit_id: str
    contract_id: str
    compliance_score: float = Field(ge=0.0, le=100.0)
    status: str  # COMPLIANT, CONDITIONAL_APPROVAL, REJECTED
    violations: List[ComplianceViolation] = Field(default_factory=list)
    atlas_vector_metrics: Dict[str, Any] = Field(default_factory=dict)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
