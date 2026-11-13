# Checkpoint Delta · NEX-M02-S06-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `75fc18bf482d0ea5dd07118082f14890545fd4f5` · **Code SHA:** `99e4ed6b9dd68237714fb27de43b4e188d08be5d`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M02-S06 concluído como pesquisa/planejamento:** matriz de 5 hipóteses com perguntas refutáveis, gaps nativos, alternativas simples, contratos de dados, custos/riscos, compatibilidade 2.5D, rollback e planos A/B/A; motor determinístico de decisão; 5 redundâncias rejeitadas.
2. **Decisões recomendadas:** 4 render features em `RESEARCH_MORE`; RenderPassport (processo) em `GO`; 5 redundâncias em `NO_GO`. Todas as decisões do Owner permanecem `PENDING`.
3. **Parent M02 (#7) permanece NOT_ADMITTED.** Nenhuma implementação, shader, addon, compositor, contrato promovido, 2.5D ou alteração de engine/CI/`project.godot`.
4. **Próximo incremento:** M02-S07 (QA visual e integração Steward) pode consolidar o atlas; experimentos A/B/A reais exigem WO própria.

## O que NÃO muda

- M01 baseline congelado; S01–S05 permanecem read-only.
- Contratos canônicos intocados; C1–C4 são drafts.
- Nenhum claim visual/FPS/VRAM; nenhuma meta do budget M01 declarada cumprida.

## Evidência de apoio

- `.engineering/evidence/NEX-M02-S06-WO-001-EVIDENCE.md`
- `docs/research/nex-m02/` (hypotheses, atlas, contracts, README, engine)
- `tests/ci/test_nex_m02_research.py` (16 testes)
