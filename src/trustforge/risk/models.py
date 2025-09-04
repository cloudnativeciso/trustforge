from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

Severity = Literal["Low", "Medium", "High", "Critical"]
Likelihood = Literal["Unlikely", "Possible", "Likely"]


@dataclass
class RiskItem:
    id: str  # e.g., R-001
    title: str  # concise risk title
    description: str  # one-paragraph description
    severity: Severity
    likelihood: Likelihood
    owner: str  # e.g., CISO
    status: Literal["Open", "Accepted", "Mitigating", "Resolved"]
    treatment: Literal["Accept", "Mitigate", "Transfer", "Avoid"]
    target_date: Optional[str] = None  # ISO date
    control_refs: Optional[list[str]] = None  # e.g., ["ID.GV-01", "PR.AC-01"]
