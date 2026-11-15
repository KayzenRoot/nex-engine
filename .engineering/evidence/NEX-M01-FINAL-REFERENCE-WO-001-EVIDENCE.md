# Evidence Bundle · NEX-M01-FINAL-REFERENCE-WO-001

**Status:** `M01_REFERENCE_LAB_EVIDENCE / NATIVE_GPU / OWNER_APPROVED_BUDGET / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M01 #6 · **Base:** `900d2b2d031a87048702625a1e98bc50905bc663`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- **Golden matrix:** 18 PNGs nativos 1920×1080 (3 cenas × 2 presets × 3 repetições), `runs.v1.json`, `SESSION-FACTS.txt`, `SHA256SUMS.txt`.
- **Performance:** 9 runs nativos 1920×1080, validação canônica 9/9 PASS, `runs.v1.json`, `SESSION-FACTS.txt`, `SHA256SUMS.txt`.
- **Builders:** `build_golden_matrix.py` e `build_performance_budget.py`, com relatórios JSON/Markdown reproduzíveis.
- **Auditoria de licenças:** `LICENSE-AUDIT.md` com 0 assets de terceiros.
- **Gate final:** `M01-FINAL-GATE.md` cobrindo S01/S03/S07 e o fechamento de #21/#23/#27/#6.
- **Governança:** `NEX-ADR-0012`, `NEX-D-022`, WO/lock/evidência/delta.

## Resultado

- **S01:** 3 imagens de aceitação (`ab-low` primeira repetição) com seed, backend, viewport e SHA-256 no relatório.
- **S03:** A/A byte-idêntico em todas as 6 células; A/B mean abs **0.4168/0.4215/0.1785**, pixels alterados **3.367%/3.354%/1.276%**, PSNR **38.485/36.851/40.464 dB**; 6 regiões por cena.
- **S07:** GPU p95 **0.139/0.151/0.122 ms**; CPU p95 **0.395/0.382/0.363 ms**; pacing p95 **4.273/4.291/4.255 ms**; 1% low **223.26/224.27/223.76 FPS**; todos os checks PASS.
- **Budget 1080p:** `OWNER_APPROVED` em 2026-11-15; meta experimental 120 FPS medida no workload de referência.
- **Licenças:** 0 assets de terceiros nas três cenas; materiais originais `StandardMaterial3D`.

## Verificação

- `build_golden_matrix.py --check`: `M01_GOLDEN_MATRIX_CHECK_PASS: 18 runs`.
- `build_performance_budget.py --check`: `M01_FINAL_BUDGET_CHECK_PASS: 9 runs`.
- Validação canônica dos 9 runs: 9/9 PASS.
- Suíte CI completa e builders/validadores verdes antes da PR.
- Nenhuma cena base, harness, preset, contrato, renderer ou shader alterado.

## O que não foi feito / não é alegado

- Nenhum jogo, gameplay, rede, cena de produção ou renderer M02–M12.
- Nenhum shader customizado, compositor, GI, sombra/VFX real.
- Nenhum claim generalizado de FPS/qualidade, cross-device ou input-to-photon.
- Aprovação `OWNER_APPROVED_ADMIN_SOLO`; não há revisor independente.

## Rollback

Reverter os evidence bundles, builders/relatórios, testes, workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e o fechamento das issues.
