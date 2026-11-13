# Definition of Done · NEX Bootstrap
Status: CANONICAL_BOOTSTRAP_DOD_VERIFIED_BY_PR74_POSTMERGE_AFTER_CHECKPOINT_PROMOTION; applies only to the GEF bootstrap, NOT to the future Godot engine.
NEX-GEF-WO-001 is done only if:
1. Current governing Source Pack is reviewed, merged and coherent.
2. The GEF CLI package is locked at v1.1.2, available locally and in reproducible CI.
3. GEF init preview is inspected, safe apply succeeds and managed state is valid.
4. CLI version/help/doctor/status results are recorded with exit codes; findings or unknowns are accounted for, not papered over.
5. Exact implementation PR HEAD has required CI passing, code/security/collision tests appropriate to risk and no unresolved known HIGH/CRITICAL.
6. Evidence Bundle, base/head SHAs, owner exact-head audit and Checkpoint Delta review are complete; merge and post-merge checks confirmed before checkpoint promotion.
A drafted plan, issue, open PR or CLI install on an unrelated machine does NOT satisfy DoD.
No scope/percentage claims for the eventual Godot-based engine.

Evidence for the bounded bootstrap DoD: [PR #74](https://github.com/KayzenRoot/nex-engine/pull/74) merged to `570d0671ed57f5cd29932baf0bac26345efca279`, exact-head CodeRabbit, Socket x2, SonarCloud, GEF Windows/Ubuntu and Governance x2 all SUCCESS, post-merge main CI six SUCCESS, owner audit comment and separate checkpoint promotion PR. Security caveats remain documented. No engine-specific DoD/percentage is inferred.

## M00 DoD is distinct from GEF DoD
The Godot M00 native baseline has now passed its distinct DoD on the reviewed PR #78 implementation and post-merge main `0c6cdbfc13bd0c1c8e80d293f7da7f2302027861`. The Godot 4.7.2 native Windows source build, local editor smokes, Ubuntu headless CI, checksums, license evidence, exact-tree equivalence, and six main checks are recorded in `.engineering/evidence/NEX-M00-WO-001-POSTMERGE-EVIDENCE.md`. Historical local 0xC0000005 root cause is UNKNOWN and risk was expressly accepted by Owner. This is an M00 baseline only, not an engine release or overall engine DoD completion. M01 requires separate admission.

## Auditoria e integração solo (Owner 2026-11-13; NEX-ADR-0004)

O DoD de uma Work Order admitida é verificável por evidências, CI, QA e auditoria técnica do administrador. **Não exige revisor humano independente nem aprovação de terceiro.** Revisões do mesmo executor são rotuladas `ADMIN_SOLO / NOT_INDEPENDENT`; não podem inventar independência, cobertura, hardware ou aprovação. O administrador delegou merge squash protegido condicional para LOW/STANDARD após: diff/fingerprints dentro do escopo, base/HEAD revalidados, CI obrigatório 100% verde, nenhuma thread pendente, testes e Evidence Bundle adequados, risco HIGH/CRITICAL inexistente, pós-merge verificado. ELEVATED/HIGH_ASSURANCE exigem testes, rollback/provas e decisão de risco documentada pelo administrador, não por um convidado externo.

O DoD de M00, do bootstrap e de futuras WOs permanecem distintos. A PR #107 integrada com limitações de viewport resize e pacing por coortes não torna o M01 parent automaticamente completo. Issues `PLANNING_ONLY/NOT_ADMITTED` não podem ser marcadas concluídas apenas por uma instrução one-shot.
