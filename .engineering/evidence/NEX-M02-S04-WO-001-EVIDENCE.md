# Evidence Bundle · NEX-M02-S04-WO-001 (TemporalGuard prototype)

**Status:** `PROTOTYPE_EVIDENCE / ANALYSIS_ONLY / NO_RENDER_THREAD / NO_COMPOSITOR / NO_SHADER / ELEVATED_RISK_DECISION_RECORDED`
**Issue:** #31 · **Base:** `bad8b52ea1a408fb9cd06e6dca2d7086d1414b07` · **Code SHA:** `9a1bdde165444b660c2a9b83e0e03234fc3a3657`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** ELEVATED

## Decisão de risco (ELEVATED, registrada)

- **Analysis/gate only:** nenhum render thread, CompositorEffect, shader, renderer core ou alteração de engine.
- **Operações irreversíveis:** nenhuma. O postprocess é estado mock desabilitado por padrão; habilitação exige defeito medido + compositor disponível; desabilitar é sempre permitido; cada análise reseta o toggle.
- **Risco residual:** qualidade temporal real (ghosting/flicker/shimmer em cenas) é `INCONCLUSIVE_NOT_RUN`.
- **Qualquer compositor/render-thread** exige WO separada do Owner, ABI pinada, evidência de falha medida e aceitação de risco. Este bundle não autoriza.

## Entregue

- `nex_modules/render3d/temporal/`: projeto Godot autocontido com `temporal_guard_analyzer.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_temporal_guard.py`: 8 testes estruturais (arquivos/projeto, API/métricas, guard/rollback, ausência de implementação de thread/compositor, marcador/evidência, decisão de risco, ausência de claim fabricado).

## Verificação executada

Comando (Godot oficial 4.7.2, binário `ab1824f8…`):

```powershell
& "<pinned Godot>" --headless --path nex_modules/render3d/temporal `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M02_S04_SMOKE_PASS: 51 checks`** (exit 0), log em `nex_modules/render3d/temporal/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 51 checks:
- configuração e limites (thresholds, min frames, max regions, render scale);
- sequência limpa → `BASELINE_ACCEPTABLE` / `KEEP_NATIVE`; métricas zero;
- passo imediato não é ghosting nem shimmer;
- ghosting injetado → `DEFECT_REPRODUCED` / `EVALUATE_COMPOSITOR`; postprocess não auto-habilitado;
- flicker injetado e shimmer injetado detectados;
- `prefer_native` → `NO_GO`;
- thresholds customizados toleram oscilação pequena;
- dados inválidos (poucos frames, região inconsistente, chave ausente, luminância fora de faixa, motion inválido, render scale inválido) → `INCONCLUSIVE` / `NO_GO`;
- penalidade de render scale registrada;
- guard de compositor: indisponível/sem defeito → rejeitado; com defeito → permitido; rollback; análise reseta estado;
- determinismo; ausência de state leak; shimmer ignora região não-edge; cap de regiões; reset limpa relatório/erro.

## O que não foi feito / não é alegado

- Sem rendering/TAA/upscale/MSAA, sem screenshots, sem gate visual humano e sem GPU/VRAM/frame-time.
- Métricas usam sequências sintéticas de luminância, não pixels reais; detectam padrões injetados, não provam qualidade de cena real.
- Linhas finas, VFX emissivos, HUD e câmera rápida reais exigem WO de integração de cena.
- Sem thread-safety claim; o código é thread-free por desenho.

## Rollback

Remover `nex_modules/render3d/temporal/**`, `tests/ci/test_temporal_guard.py`, este bundle e o delta. Nenhum arquivo de M01, S01–S03, contratos, CI ou checkpoint é alterado.

## Próximos passos

- M02-S05 (matriz de capacidades nativas/perfis gráficos) pode consumir o analyzer/gate como mock.
- Qualquer CompositorEffect exige WO separada e aceitação de risco do Owner.
- Medições reais usam o baseline M01 e o mesmo hardware/procedimento.
