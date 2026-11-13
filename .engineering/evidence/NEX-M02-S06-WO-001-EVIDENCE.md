# Evidence Bundle · NEX-M02-S06-WO-001 (R&D decision atlas)

**Status:** `RESEARCH_EVIDENCE / NO_IMPLEMENTATION / NO_MEASURED_CLAIM / OWNER_DECISIONS_PENDING`
**Issue:** #33 · **Base:** `75fc18bf482d0ea5dd07118082f14890545fd4f5` · **Code SHA:** `f1340378ca46454a6e41fa41e0b232de1a47adf1`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** LOW

## Entregue

- `docs/research/nex-m02/hypotheses.v1.json`: 5 hipóteses com pergunta refutável, gap nativo, alternativa simples, contrato de dados, custo/risco, compatibilidade 2.5D, rollback, plano A/B/A, métricas, fontes Godot e `owner_decision=PENDING`.
- `docs/research/nex-m02/tools/decision_engine.py`: regras determinísticas (`--check`).
- `docs/research/nex-m02/DECISION-ATLAS.md`: matriz de decisão e redundâncias rejeitadas.
- `docs/research/nex-m02/proposed-contracts.md`: contratos C1–C4 `DRAFT_NOT_PROMOTED`.
- `tests/ci/test_nex_m02_research.py`: 16 testes (documento, atlas, contratos, regras do motor, determinismo).

## Verificação executada

```powershell
python docs/research/nex-m02/tools/decision_engine.py --check
python -m unittest tests/ci/test_nex_m02_research.py -v
```

Resultado:
- `NEX-M02-RD-ISO: RESEARCH_MORE (EVIDENCE_NOT_MEASURED)`
- `NEX-M02-RD-SIGHT: RESEARCH_MORE (EVIDENCE_NOT_MEASURED)`
- `NEX-M02-RD-DEPTH: RESEARCH_MORE (EVIDENCE_NOT_MEASURED)`
- `NEX-M02-RD-TEMP: RESEARCH_MORE (EVIDENCE_NOT_MEASURED)`
- `NEX-M02-RD-PASS: GO (PROCESS_TOOL_PROTOTYPE_VERIFIED)`
- `HYPOTHESES_OK`
- Testes: **16/16 PASS**.

## Decisões e rejeições

| Item | Recomendação | Fundamentação |
|---|---|---|
| IsoDirector / Sightline / DepthWeave / TemporalGuard | RESEARCH_MORE | nenhum gap nativo medido; A/B/A em cena real necessário |
| RenderPassport (ferramenta de processo) | GO | protótipo verificado, rollback, sem mudança de rendering; decisão do Owner pendente |
| Custom mesh LOD / occlusion culling | NO_GO | nativo existe; tuning é M06 |
| Custom TAA/upscaler | NO_GO | opções nativas primeiro; sem gap medido |
| Global z-depth hack | NO_GO | passes e conflitos explícitos são seguros |
| GPU-driven core C++ | NO_GO | ELEVATED; RFC + benchmark + Steward lock |

## Limites

- Nenhuma implementação, shader, addon, compositor, 2.5D ou alteração de engine/contrato/CI/`project.godot`.
- Nenhum valor medido, ganho visual ou FPS é alegado; sem rendering/benchmark.
- O motor recomenda; não aprova, não promove contrato e não decide pelo Owner.
- Contratos C1–C4 são drafts; promoção exige WO específica, revisão e lock.

## Rollback

Remover `docs/research/nex-m02/**`, `tests/ci/test_nex_m02_research.py`, este bundle e o delta. Nenhum arquivo de M01/S01–S05, contratos, CI ou checkpoint é alterado.

## Próximos passos

- Owner decide cada hipótese após evidência A/B/A real.
- M02-S07 (QA visual/integração Steward) pode consolidar o atlas como insumo.
- Qualquer experimento real usa o baseline M01 e o mesmo hardware/procedimento.
