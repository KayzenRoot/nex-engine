# Evidence Bundle · NEX-M05-FXBUDGET-WO-001 (FX-budget planner)

**Status:** `PROTOTYPE_EVIDENCE / PLANNING_ONLY / NO_PARTICLES / NO_RENDERING / NO_VISUAL_CLAIM`
**Issue:** #10 · **Base:** `6f93034e7557a6cb0a77aa89d6109ffea9d0c3da` · **Code SHA:** `10ecb58afc411f4e5a6e421342dffdd29462c0ab`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/vfx/fxbudget/`: projeto Godot autocontido com `fx_budget_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_fx_budget_planner.py`: 9 testes estruturais (arquivos/projeto, API, vocabulário `spellfx.v1`, vereditos/achados/ações, ausência de partículas/rendering, marcador/evidência, limites, ausência de claim visual).

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/vfx/fxbudget `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M05_FXBUDGET_SMOKE_PASS: 57 checks`** (exit 0), log em `nex_modules/vfx/fxbudget/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 57 checks:
- configuração de emissores/partículas/GPU/decals e rejeição de limites;
- conjunto vazio, agregação de 2 magias (7 emissores, 484 partículas, 3 GPU, 2 decals, 1 light bridge) e detalhe por magia ordenado;
- orçamento de partículas excedido, plano de redução em rodadas, projeção dentro do orçamento e recomendação;
- orçamento GPU excedido, conversão GPU→CPU dos menores emissores e projeção;
- orçamentos de emissores e decals, recomendações correspondentes;
- veredito `TIGHT` a 90%;
- validação: emitter duplicado, impact ausente, autoridade visual_only, light bridge mismatch, elemento inválido, duração > 60000 ms, fase duplicada, id curto, amount acima do limite, light amount 0, decal policy acima do budget, autoridade ausente e fase sem emissores → `INVALID_INPUT` com razão;
- determinismo, último relatório e `clear()`.

## O que não foi feito / não é alegado

- Nenhuma partícula, emissor, luz, decal, shader ou cena criada; nenhum `GPUParticles3D`/`CPUParticles3D`/`RenderingServer`.
- Totais de partículas são aritméticos, não partículas vivas, overdraw ou fill rate.
- Conversão GPU→CPU é sugestão de planejamento, não trade-off medido; merge de emissores e redução de decals não têm cena projetada.
- Qualidade visual/clareza de combate e runtime: `INCONCLUSIVE_NOT_RUN`.
- M05 parent (#10) permanece `NOT_ADMITTED`.

## Rollback

Remover `nex_modules/vfx/fxbudget/**`, `tests/ci/test_fx_budget_planner.py`, este bundle, o delta e a WO/lock correspondentes. Nenhum estado de engine, contrato ou checkpoint é alterado.

## Próximos passos

- Validação real de FX exige WO de cena/partículas com GPU.
- M06/M08/M12 permanecem não admitidos.
