# Evidence Bundle · NEX-M07-S01-WO-001 (Canvas/batching planner)

**Status:** `PROTOTYPE_EVIDENCE / PLANNING_ONLY / NO_RENDERING / NO_SHADER / NO_PERFORMANCE_CLAIM`
**Issue:** #12 · **Base:** `04f0108e004d31984758acf32069f285240f2489` · **Code SHA:** `817cfcfdcc0d3c90a03ef53ef82a325d6e501492`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/render2d/canvas/`: projeto Godot autocontido com `canvas_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_render2d_planner.py`: 8 testes estruturais (arquivos/projeto, API, vocabulário do contrato render2d.v1, ausência de rendering, marcador/evidência, limites, ausência de claim fabricado).

## Verificação executada

```powershell
& "<pinned Godot>" --headless --path nex_modules/render2d/canvas `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M07_S01_SMOKE_PASS: 46 checks`** (exit 0), log em `nex_modules/render2d/canvas/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 46 checks:
- configuração e limites (layers, draw calls, lights);
- materiais: registro, duplicata, ids vazios, lighting mode inválido;
- camadas: duplicata, material desconhecido, blend/z inválidos, escala zero, posição não finita, cap;
- ordenação por z e desempate por id; invisíveis excluídas;
- batching: material/blend iguais agrupam; material ou blend diferentes separam; materiais intercalados geram 3 batches;
- draw calls e state changes coerentes;
- partículas: emissor ativo adiciona draw call; inativo não; emitting com amount 0 rejeitado;
- luzes: contagem, duplicata, tipo/energia inválidos, aviso de orçamento, aviso de layer iluminada sem luz;
- orçamento de draw calls; plano determinístico; limitações; plano vazio após clear.

## O que não foi feito / não é alegado

- Sem rendering real (CanvasItem/shader/material/light/particle); draw calls são estimativa determinística, não medição de GPU.
- Performance/frame-time/VRAM: `INCONCLUSIVE_NOT_RUN`.
- Batching simples por material/blend consecutivos; sem atlas, cache de estado, y-sort ou rasterização.
- Sem integração em cena, M04/M05/M08/2.5D, engine ou contratos.
- O vocabulário do contrato `render2d.v1` é espelhado, não redefinido.

## Rollback

Remover `nex_modules/render2d/canvas/**`, `tests/ci/test_render2d_planner.py`, este bundle e o delta. Nenhum arquivo de M01/M02, contratos, CI ou checkpoint é alterado.

## Próximos passos

- Integração 2D real em cena exige WO própria.
- M04 (materiais), M05 (VFX) e M08 (2.5D) permanecem não admitidos; o contrato M07 é o insumo.
- Qualquer medição futura usa o baseline M01 e o mesmo hardware/procedimento.
