# Decisions Ledger / ADRs
Status: DRAFT for first planning review. Preserve decisions verbatim until explicitly superseded.
- NEX-D-001 [OWNER_DIRECTIVE / PROPOSED CANONICAL]: project is `nex-engine` in `KayzenRoot`.
- NEX-D-002 [OWNER_DIRECTIVE / PROPOSED CANONICAL]: future engine is a Godot-based customized distribution; new game is native desktop rather than browser-first. This is future vision, not a currently admitted Godot implementation.
- NEX-D-003 [OWNER_DIRECTIVE / CURRENT WORK]: initial increment is ONLY install and validate GEF Bootstrap latest production-accepted release.
- NEX-D-004 [SOURCE-VERIFIED]: upstream latest production-accepted stable package is `@gef-bootstrap/cli@1.1.2`, release tag `v1.1.2` resolves to commit `af1fe9371a3883cbd8a4aafcbb405ddcd4c2ca82` (2026-10-02).
- NEX-D-005 [PROPOSED PROCESS]: follow GEF ADR-0008 Codex-only implementation, ChatGPT governance/planning/exact-head owner audit.
No design/performance claim about a future engine is approved by this bootstrap phase.

- NEX-D-006 [OWNER_DIRECTIVE / 2026-10-10 / SPECIFIC EXCEPTION]: for NEX-GEF-WO-001 bootstrap ONLY, ChatGPT is directly authorized to author repository integration, installation scripts, CI and tests through GitHub. Codex will be used for future engine improvements. This explicitly supersedes NEX-D-005 for this bounded bootstrap increment; does not modify upstream GEF policy and does not authorize future implementation without a Work Order.
