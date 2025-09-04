from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class CsfControl:
    function: str  # e.g., IDENTIFY
    category: str  # e.g., GV (Govern)
    subcategory_id: str  # e.g., ID.GV-01
    title: str  # brief title
    description: str  # concise description


def nist_csf20_controls() -> Iterable[CsfControl]:
    """
    Minimal seed set to prove the pipeline.
    You can extend/replace this with the full catalog later.
    """
    data: List[CsfControl] = [
        CsfControl(
            function="IDENTIFY",
            category="GV",
            subcategory_id="ID.GV-01",
            title="Governance program established",
            description="Roles, responsibilities, and authorities established and communicated.",
        ),
        CsfControl(
            function="PROTECT",
            category="PR",
            subcategory_id="PR.AC-01",
            title="Identity management",
            description="Identities are issued, managed, verified, revoked for users and services.",
        ),
        CsfControl(
            function="DETECT",
            category="DE",
            subcategory_id="DE.AE-01",
            title="Anomalies detected",
            description="Potential cybersecurity events are detected in a timely manner.",
        ),
        CsfControl(
            function="RESPOND",
            category="RS",
            subcategory_id="RS.MA-01",
            title="Incident response plan",
            description="Documented IR plan with roles, communications, and procedures.",
        ),
        CsfControl(
            function="RECOVER",
            category="RC",
            subcategory_id="RC.CO-01",
            title="Recovery planning",
            description="Documented recovery plans are maintained and tested.",
        ),
    ]
    return data
