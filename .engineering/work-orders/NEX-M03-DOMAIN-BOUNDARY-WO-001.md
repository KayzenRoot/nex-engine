# NEX-M03-DOMAIN-BOUNDARY-WO-001 | Fronteira de domínio do modelo de luz

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005); M03 é `BOUNDED_ADMITTED_ANALYSIS_PIPELINE` desde NEX-ADR-0007.
**Base:** `main` `3a3b0f19d8e9e61e9eed4121391f0bc5a698e580`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (análise de evidência).
**Lock:** `.engineering/context-locks/NEX-M03-DOMAIN-BOUNDARY-WO-001-EXECUTION.json`.

## Objetivo

Quantificar a fronteira de domínio do `nex_light_cost_model.v1` usando o bundle `res-scaling` já integrado: o modelo não tem termo de resolução, então o previsto é constante enquanto o GPU p95 medido cresce de 960×540 para 1920×1080. O relatório testa se o único acerto em 2% é específico da resolução de calibração (1280×720), sem nova medição e sem alterar o modelo.

## Escopo

- `docs/benchmarks/m03/tools/build_budget_validation.py`: modos `--domain` e `--check-domain`; saída curada inalterada.
- `docs/benchmarks/m03/budget-domain-boundary.v1.json` e `BUDGET-DOMAIN-BOUNDARY.md`: 6 células da arena em três resoluções.
- `docs/benchmarks/m03/README.md`: arquivos, método, uso e limitações.
- `tests/ci/test_m03_domain_boundary.py`: 6 testes de cobertura, invariância, veredito e reprodutibilidade.
- `tests/ci/test_builder_check_enforcement.py` e `.github/workflows/nex-ci-fastlane.yml`: enforcement de `--check-domain` (21 comandos / 18 arquivos).
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Alterar coeficientes, snapshot, GDScript, contrato `lighting.v1` ou modelo.
- Nova medição, captura, renderização, cena ou harness.
- Alterar `m01-ab.v1.json`, `res-scaling.v1.json` ou qualquer bundle M09.
- Novos parents, runtime, renderer, shaders, hub, `project.godot`.
- Claims de FPS, qualidade, ganho ou generalização cross-device/sessão.

## DoD

- 6 células (2 presets × 3 resoluções), previsto invariante e medido crescente.
- Único acerto em 2% em `ab-high`/1280×720; veredito `CALIBRATION_RESOLUTION_MATCH_ONLY`.
- Deltas medidos 960→1920: +0.060 ms (+62.5%) ab-low e +0.509 ms (+160.6%) ab-high; previsto 0.0 ms.
- `--check` e `--check-domain` PASS; saída curada byte-idêntica.
- Suítes CI/contratos/telemetria verdes em worktree LF limpo; PR protegida e checkpoint pós-merge.

## STOP

- Base/HEAD divergente, bundle com workload inesperado, mais de um acerto em 2%, divergência da saída curada, necessidade de nova medição ou check vermelho → parar e registrar.
