# Checkpoint Delta · NEX-M09-VISUAL-1920-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `06eb6d92da50bdb8105bbc8f7b6bed98faebb329`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-VISUAL-1920 integrado:** 18 PNGs das três cenas M01 em 1920×1080, A/A byte-idêntico e comparação A/B.
2. **Medição:** A/B mean abs 0.4168/0.4215/0.1785 e changed pixels 3.367%/3.354%/1.276% (corridor/arena/city); diferenças ligeiramente menores que em 1280×720.
3. **Atlas atualizado:** 9 bundles, 36 imagens, 351 arquivos e 9 source SHAs.
4. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine, cenas base, `project.godot` ou CI.
5. **Sem claim de qualidade:** frame estático, sessão única, comparação RGB byte a byte.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-VISUAL-1920-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-1920/`
- `docs/benchmarks/m09/m01-visual-1920.v1.json` e `M01-VISUAL-1920-REPORT.md`
- `tests/ci/test_m01_visual_1920.py` (9 testes)
