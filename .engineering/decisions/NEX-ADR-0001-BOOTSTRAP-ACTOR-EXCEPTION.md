# NEX-ADR-0001 · Owner bootstrap executor exception
Status: OWNER_DIRECTED / ACCEPTED_ON_GOVERNANCE_PR_MERGE, not active until merged. Date: 2026-10-10.
Decision: ChatGPT performs the complete first GEF Bootstrap v1.1.2 installation/integration within the GitHub repository, including minimal scripts, package pinning, CI, test fixes and evidence. This is a one-Work-Order exception for NEX-GEF-WO-001 to the inherited GEF ADR-0008 Codex-only software-author rule.
Rationale: Owner wants Codex used only after the bootstrap is operational, for future improvement of the Godot-based engine. User requested this change explicitly in live conversation.
Scope: KayzenRoot/nex-engine, initial GEF Bootstrap release only. No change to upstream KayzenRoot/gef-bootstrap, no general authorization for rendering/game code.
Constraints: Inspect and preserve Git/source state, only NECESSARY files, evidence-bound checks, distinct implementation PR, no bypass/force push, no external paid services or real auth, no unauthorized deployment to user's personal PC.
Authoritative ordering: This ADR supersedes only NEX-D-005 actor choice and conflicting wording in the draft Source Pack for NEX-GEF-WO-001. All safety, CI, review and checkpoint gates remain.
Post-bootstrap: Codex is preferred for Godot engine improvements and other newly admitted implementation Work Orders unless separately amended.
Acceptance: planning governance PR audited at exact HEAD, accepted and promoted; implementation issue/Work Order refreshed to the next exact main SHA. Do not confuse owner directive with accepted runtime evidence.
