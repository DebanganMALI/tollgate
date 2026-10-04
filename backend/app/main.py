from fastapi import FastAPI

from app.policy.engine import PolicyEngine
from app.policy.models import Decision, PaymentProposal

app = FastAPI(title="Tollgate", version="0.1.0")
engine = PolicyEngine()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/policy/evaluate")
def evaluate(proposal: PaymentProposal) -> Decision:
    return engine.evaluate(proposal)
