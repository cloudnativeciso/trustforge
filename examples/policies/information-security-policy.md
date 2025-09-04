---
title: "Information Security Policy"
subtitle: "Cloud-Native & AI-Safe"
version: "1.2.0"
owner: "CISO"
last_reviewed: "2025-09-01"
applies_to: ["All Employees", "Contractors"]
refs:
  - "NIST CSF 2.0"
  - "SOC 2 (CC Series)"
footer: "cloudnativeciso.com · security@cloudnativeciso.com"
---

# Purpose
This policy defines Cloud Native CISO’s approach to protecting information assets across cloud platforms and AI workloads. It applies to SaaS services, CI/CD, infrastructure-as-code (IaC), and internal tooling used to deliver our products.

## Scope
This policy covers:
- Production and pre-production cloud environments (AWS and GCP)
- Kubernetes clusters and workloads
- LLM-enabled services, agents, and prompt workflows
- Source code, secrets, and build artifacts
- End-user data and internal business data

# Policy
1. **Risk-based controls** are selected and maintained according to NIST CSF 2.0 functions (Identify, Protect, Detect, Respond, Recover).
2. **Least privilege** is enforced for human and workload identities across cloud providers and GitHub.
3. **Data protection** includes encryption in-transit and at-rest using managed KMS and key rotation.
4. **Change management** is implemented via pull requests, code review, and automated security checks (SAST, IaC scanning).
5. **Incident response** procedures are documented, tested, and improved after every event.

## AI Security Safeguards
- Inputs to LLMs are sanitized, logged, and evaluated for prompt-injection indicators.
- Output from LLMs that may trigger actions is constrained by **allow lists** and **schema validation**.
- Secrets are never passed to LLM contexts; redaction and tokenization are enforced by middleware.
- Model configurations and datasets are change-controlled and peer reviewed.

## Cloud-Native Controls
- **Kubernetes**: Admission controls, image signing/verification, and restricted network policies (deny-by-default).
- **AWS/GCP IAM**: Short-lived credentials, workload identity, SCP/Org Policy guardrails.
- **Data**: Customer data is logically segregated by tenant; access is logged and reviewed.
- **Monitoring**: Centralized logs and metrics with alerting thresholds; anomaly detection for auth and network events.

# Roles & Responsibilities
- **CISO**: Owns the program, policy updates, and exception approvals.
- **Security Engineering**: Designs controls, threat models, and detection content.
- **Platform**: Implements guardrails in IaC and CI/CD, remediates vulnerabilities.
- **All Staff**: Follow the policy; report suspected incidents within one business day.

# Review
This policy is reviewed at least annually, or after material changes to architecture, regulations, or incident learnings.
