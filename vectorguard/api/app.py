"""
FastAPI Application for VectorGuard: Enterprise Policy & Contract Radar.
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from vectorguard.models.policy import (
    ContractAuditRequest,
    ContractAuditResult,
    PolicyClause,
)
from vectorguard.engine.radar_agent import VectorGuardRadarAgent

app = FastAPI(
    title="VectorGuard: Autonomous Enterprise Compliance & Contract Policy Radar",
    description="Vector-Driven Policy Compliance Engine powered by MongoDB Atlas Vector Search ($40k Prize Pool)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

radar_agent = VectorGuardRadarAgent()
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "VectorGuard Atlas Vector Radar",
        "competition": "MongoDB AI Innovators Challenge ($40,000 Prize Pool)",
        "vector_index": "MongoDB Atlas Vector Search (Cosine KNN)",
    }


@app.post("/api/audit/contract", response_model=ContractAuditResult)
async def audit_contract_endpoint(request: ContractAuditRequest):
    try:
        result = await radar_agent.audit_contract(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sample/contracts")
async def get_sample_contracts():
    return [
        {
            "id": "compliant_dpa",
            "contract_id": "CTR-2025-001",
            "title": "Cloud Services Data Processing Agreement (DPA)",
            "counterparty": "Global SaaS Enterprise Inc.",
            "contract_type": "DPA",
            "clauses": [
                {
                    "clause_id": "SEC-1",
                    "section_title": "Scope of Processing",
                    "text": "The Processor shall only process personal data on documented instructions from the controller.",
                    "category": "PRIVACY",
                },
                {
                    "clause_id": "SEC-2",
                    "section_title": "Security Incident Notification",
                    "text": "In the event of a confirmed personal data breach, Processor shall notify Controller in writing within 72 hours of becoming aware.",
                    "category": "COMPLIANCE",
                },
                {
                    "clause_id": "SEC-3",
                    "section_title": "Data Deletion upon Termination",
                    "text": "Upon termination of services, Processor shall delete or return all customer personal data within thirty (30) days.",
                    "category": "PRIVACY",
                },
            ],
        },
        {
            "id": "predatory_vendor_trap",
            "contract_id": "CTR-TRAP-999",
            "title": "High-Risk AI Vendor Master Service Agreement",
            "counterparty": "Apex Cloud Analytics Ltd",
            "contract_type": "VENDOR_MSA",
            "clauses": [
                {
                    "clause_id": "TRAP-1",
                    "section_title": "Data Retention & IP",
                    "text": "Vendor reserves the right to unilateral retention of customer personal data after termination to train proprietary foundation models.",
                    "category": "PRIVACY",
                },
                {
                    "clause_id": "TRAP-2",
                    "section_title": "Breach Notification",
                    "text": "Customer agrees to waive data breach notification obligations unless criminal negligence is proven by a federal court.",
                    "category": "COMPLIANCE",
                },
                {
                    "clause_id": "TRAP-3",
                    "section_title": "Indemnification",
                    "text": "Customer shall indemnify vendor for vendor negligence arising out of platform data processing operations.",
                    "category": "INDEMNITY",
                },
            ],
        },
    ]


@app.get("/")
async def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"message": "VectorGuard API live."})
