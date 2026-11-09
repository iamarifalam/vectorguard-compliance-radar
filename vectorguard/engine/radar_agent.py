"""
Radar Agent: Orchestrates contract clause auditing using MongoDB Atlas Vector Search.
"""

import time
from typing import List
from vectorguard.models.policy import (
    ContractAuditRequest,
    ContractAuditResult,
    ComplianceViolation,
)
from vectorguard.engine.vector_store import AtlasVectorIndex, generate_semantic_embedding, cosine_similarity


class VectorGuardRadarAgent:
    def __init__(self):
        self.atlas_index = AtlasVectorIndex()

    async def audit_contract(self, request: ContractAuditRequest) -> ContractAuditResult:
        t_start = time.time()
        violations: List[ComplianceViolation] = []

        total_clauses = len(request.clauses)
        vectors_computed = 0

        for clause in request.clauses:
            vectors_computed += 1
            clause_lower = clause.text.lower()
            nearest = self.atlas_index.search_nearest_mandate(clause.text, k=1)

            if not nearest:
                continue

            best_mandate, similarity = nearest[0]

            # 1. Check for forbidden liability or compliance traps
            for forbidden in best_mandate.get("forbidden_terms", []):
                for keyword in forbidden.split():
                    if len(keyword) > 4 and keyword in clause_lower:
                        if any(trap in clause_lower for trap in ["unilateral", "waive", "uncapped", "unencrypted", "single-factor", "retention"]):
                            violations.append(
                                ComplianceViolation(
                                    violation_id=f"VIOL-{clause.clause_id}",
                                    severity="CRITICAL",
                                    clause_id=clause.clause_id,
                                    rule_breached=f"Unlawful waiver or risk transfer conflicting with {best_mandate['rule_id']}",
                                    matched_mandate=best_mandate["mandate"],
                                    similarity_score=round(similarity, 3),
                                    risk_narrative=f"Clause contains dangerous risk attribution: '{forbidden}'. Violates standard regulatory requirements.",
                                    remediation_clause=(
                                        f"Replace with standard {best_mandate['rule_id']} compliant language: "
                                        f"'{best_mandate['required_terms'][0]}'."
                                    ),
                                )
                            )
                            break

            # 2. Check for missing breach notification window in DPA
            if "breach" in clause_lower and "hours" not in clause_lower and "72" not in clause_lower:
                violations.append(
                    ComplianceViolation(
                        violation_id=f"VIOL-NOTIF-{clause.clause_id}",
                        severity="HIGH",
                        clause_id=clause.clause_id,
                        rule_breached="GDPR Article 33/34 Incident Notification Window Missing",
                        matched_mandate="GDPR Article 28 / 33 Breach Governance",
                        similarity_score=round(similarity, 3),
                        risk_narrative="Data breach notification is vague or lacks strict statutory 72-hour delivery timetable.",
                        remediation_clause="Insert explicit obligation: 'Vendor shall notify Customer in writing within seventy-two (72) hours of confirming any Security Incident.'",
                    )
                )

            # 3. Check for uncapped indemnity
            if "indemn" in clause_lower and any(w in clause_lower for w in ["sole liability", "customer shall indemnify vendor for vendor negligence"]):
                violations.append(
                    ComplianceViolation(
                        violation_id=f"VIOL-INDEMN-{clause.clause_id}",
                        severity="CRITICAL",
                        clause_id=clause.clause_id,
                        rule_breached="Unilateral Negligence Indemnification Trap",
                        matched_mandate="Commercial Indemnification Standard",
                        similarity_score=round(similarity, 3),
                        risk_narrative="Forces customer to indemnify vendor against vendor's own gross negligence or willful misconduct.",
                        remediation_clause="Insert standard carve-out: 'Except to the extent caused by Vendor's gross negligence, willful misconduct, or breach of confidentiality obligations.'",
                    )
                )

        # Score calculation
        score = 100.0
        critical_count = sum(1 for v in violations if v.severity == "CRITICAL")
        high_count = sum(1 for v in violations if v.severity == "HIGH")

        score -= (critical_count * 35.0)
        score -= (high_count * 15.0)
        score = max(0.0, min(100.0, score))

        if score >= 85.0 and critical_count == 0:
            status = "COMPLIANT"
        elif score >= 50.0:
            status = "CONDITIONAL_APPROVAL"
        else:
            status = "REJECTED"

        audit_id = f"VG-AUDIT-{request.contract_id}-{int(time.time())}"

        return ContractAuditResult(
            audit_id=audit_id,
            contract_id=request.contract_id,
            compliance_score=round(score, 1),
            status=status,
            violations=violations,
            atlas_vector_metrics={
                "index_type": "MongoDB Atlas Vector Search (KNN)",
                "embedding_dimensions": 64,
                "similarity_metric": "cosine",
                "clauses_evaluated": total_clauses,
                "vectors_computed": vectors_computed,
                "search_latency_ms": round((time.time() - t_start) * 1000, 2),
            },
        )
