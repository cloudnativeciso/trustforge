---
title: "Information Security Policy"
subtitle: "v1.0"
author: ["Cloud Native CISO — Security Team"]
version: "1.0"
status: "Draft"
owner: "CISO"
confidentiality: "Internal"
---

# Purpose
This policy establishes the baseline controls that protect our data, systems, and customers.

# Scope
This policy applies to all personnel, contractors, and systems operated by or on behalf of the Organization.

# Roles & Responsibilities
- **CISO**: Owns this policy; ensures reviews/approvals.
- **Engineering**: Implements technical controls; reports exceptions.
- **All Personnel**: Follow this policy and report incidents.

# Policy
1. **Identity & Access**: MFA is required for all production-access accounts.
2. **Secrets**: Secrets must not be hardcoded; approved secret managers are required.
3. **Vulnerability Mgmt**: Critical vulnerabilities must be remediated within defined SLAs.
4. **Logging**: Security-relevant logs must be retained for at least 90 days.
5. **Change Mgmt**: All production changes must go through version control and CI.

# Exceptions
Temporary exceptions require documented justification, compensating controls, and an expiry date.

# Review & Approval
This policy is reviewed at least annually or upon significant changes to the business or threat landscape.
