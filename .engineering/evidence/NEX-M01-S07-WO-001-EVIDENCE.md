# Evidence Bundle · NEX-M01-S07-WO-001 (audit pack / baseline freeze)

**Status:** `AUDIT_PACK_PROPOSED / NOT_A_CHECKPOINT_PROMOTION`
**Issue:** #27 · **Base:** `871fd1bc89c272ba04327ddc81e407d35ff5fee0` · **Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Pack:** `docs/benchmarks/m01/` · **Manifest:** 71 artefatos com SHA-256 de blobs Git.

## Entregue

- `manifest.json` — índice verificável (caminho + SHA-256 + bytes) de toolchain, contratos, S02 fixture, S03 comparador, S04 relatórios/capturas, S05 15 capturas + validações, S06 docs, QA report/resultados, budget.
- `BASELINE.md`, `PERFORMANCE-BUDGET.md`, `budget.v1.json`, `RISKS.md`, `DEVIATIONS.md`, `CI_LINKS.md`, `research.md`, índices `runs/`, `visual/`, `stress/`.
- `tools/build_manifest.py` — recalcula hashes a partir do índice Git (imune a CRLF local) e `--check` falha em divergência.
- `tests/ci/test_m01_baseline_audit.py` — 10 testes: identidade, claims falsos, hashes, reprodutibilidade, matrizes, budget, documentos, CI links.

## Verificação executada

- `python docs/benchmarks/m01/tools/build_manifest.py --check` → `MANIFEST_OK artifacts=71`.
- Manifesto reprodutível a partir do índice Git; hashes comparados byte a byte.
- Matrizes: S04 12/12 COMPLETE (Run9 INVALID documentado), S05 15/15 COMPLETE (baseline-25 ×3).
- Budget: tetos > medidos; metas 60/120 marcadas `ASPIRATIONAL_NOT_MEASURED`; claims todos falsos.
- Testes locais: `tests/ci` com o novo arquivo; suíte completa em worktree LF (registrada no PR).
- Nenhum código do engine, contrato, CI ou checkpoint alterado por este WO (delta apenas proposto).

## Limitações e disciplina

- Não declara conclusão do engine, do parent M01 ou de M02–M12.
- Não declara meta de FPS atingida; runs são 1280×720/VSync.
- Não usa Docker/cloud como benchmark; CI headless é smoke.
- `RENDERER_ALLOCATION_BYTES` não é VRAM; comparação entre sessões de pacing é proibida.
- O delta de checkpoint é **proposto**; promoção exige decisão do Owner e auditoria pós-merge.

## Próximo passo

Com o baseline congelado, o próximo incremento legal é uma admissão explícita do Owner: S07 está concluído; M02-S01 (câmera) tem contrato e baseline, mas exige Work Order própria. Nenhuma implementação de módulo é autorizada por este bundle.
