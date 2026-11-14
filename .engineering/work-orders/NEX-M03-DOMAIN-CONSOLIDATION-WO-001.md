# NEX-M03-DOMAIN-CONSOLIDATION-WO-001 | Consolidação da fronteira de domínio M03

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005); M03 é `BOUNDED_ADMITTED_ANALYSIS_PIPELINE` desde NEX-ADR-0007.
**Base:** `main` `0683631df4e047bfff2bf8a0c45dd6b0df9853dd`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (análise de evidência).
**Lock:** `.engineering/context-locks/NEX-M03-DOMAIN-CONSOLIDATION-WO-001-EXECUTION.json`.

## Objetivo

Consolidar no relatório `--domain` as duas novas evidências M09: **200 proxies em 1280×720** e **2560×1440**. O relatório passa a mostrar que o acerto de 2% do `ab-high` é a mesma célula de calibração em 100 e 200 proxies, e que ele não sobrevive a 2560×1440. Sem nova medição e sem alterar o modelo.

## Escopo

- `docs/benchmarks/m03/tools/build_budget_validation.py`: helpers `_load_model`, `_domain_cell`, `_evidence_cells`, `_cell_table_lines`; blocos `proxy_robustness` e `high_resolution`.
- `docs/benchmarks/m03/budget-domain-boundary.v1.json` e `BUDGET-DOMAIN-BOUNDARY.md` regenerados.
- `docs/benchmarks/m03/README.md`: arquivos, método e limitações.
- `tests/ci/test_m03_domain_boundary.py`: 7 testes.
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Nova medição, captura, renderização ou mudança de cena/harness.
- Alterar coeficientes, snapshot, GDScript, contrato `lighting.v1`, bundles M09 ou modelo.
- Novos parents, runtime, renderer, shaders, hub, `project.godot`.
- Claims de FPS, qualidade, ganho ou generalização cross-device/sessão.

## DoD

- Grid de resolução com 6 células; 200/1280 com 2 células; 2560×1440 com 2 células.
- `ab-high`/1280×720 dentro de 2% em 100 e 200 proxies; 2560×1440 com 0 acertos.
- `within_2pct_total = 2`; veredito `CALIBRATION_RESOLUTION_MATCH_ONLY`.
- `--check` e `--check-domain` PASS; suítes CI/contratos/telemetria verdes; 23/23 builders.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, evidência M09 ausente/inválida, mais de um acerto no grid, divergência da saída curada ou check vermelho → parar e registrar.
