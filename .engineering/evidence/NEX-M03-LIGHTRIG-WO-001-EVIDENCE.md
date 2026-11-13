# Evidence Bundle · NEX-M03-LIGHTRIG-WO-001 (Deterministic light-rig planner)

**Status:** `PROTOTYPE_EVIDENCE / PLANNING_ONLY / NO_RENDERING / NO_SHADOW_IMPLEMENTATION / NO_PERFORMANCE_CLAIM`
**Issue:** #8 · **Base:** `edd3bc3003acae681f46227367d8c11b06cad99f` · **Code SHA:** `9c252e8062141f90f7c30e156b0ff35eee1fb4ab`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/lighting/light_rig/`: projeto Godot autocontido com `light_rig_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_light_rig_planner.py`: 10 testes estruturais (arquivos/projeto, API, vocabulário `lighting.v1`, limites do contrato, campos obrigatórios da observação, ausência de rendering, marcador/evidência, limites documentados, ausência de claim fabricado de performance).

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/lighting/light_rig `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M03_LIGHTRIG_SMOKE_PASS: 70 checks`** (exit 0), log em `nex_modules/lighting/light_rig/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 70 checks:
- configuração: limites de luzes, sombras, cascatas e atlas; restauração de defaults;
- ambiente: atualização parcial, rejeição de ambient source/tonemap/energia/fog/GI inválidos;
- registro: id vazio/duplicado, tipo, cor, energia, bias, softness, cull mask e caps;
- coerência por tipo: directional sem range/spot angle, omni sem spot angle/cascatas, spot angle ≤ 90°, range ≤ 200 m;
- sombras: caster sem energia rejeitado; slots por energia desc com desempate por id; orçamento, demotion e aviso;
- cascatas: overflow avisado e clamp determinístico; estimativa de shadow maps;
- plano: ordenação por id, contagens por tipo, vocabulário do contrato, determinismo, limitações, orçamento de luzes;
- exportação: `lighting.v1` com performance `UNAVAILABLE`, proveniência validada (SHA/capture/evidence), campos exclusivos do planner omitidos;
- clear: remove luzes e restaura ambiente default.

## O que não foi feito / não é alegado

- Nenhuma luz, shadow map, GI probe, shader, material ou cena criada; nenhum arquivo em `nex_bench/**`, engine ou CI alterado.
- `estimated_shadow_maps` é aritmética determinística, não medição de GPU.
- Performance/qualidade/frame-time/VRAM: `INCONCLUSIVE_NOT_RUN`.
- Atribuição de sombras é política de planejamento; sem atlas packing, cascade fitting ou contact shadows.
- M03 parent (#8) permanece `NOT_ADMITTED`; integração real exige WO própria.

## Rollback

Remover `nex_modules/lighting/light_rig/**`, `tests/ci/test_light_rig_planner.py`, este bundle, o delta e a WO/lock correspondentes. Nenhum estado de engine, contrato ou checkpoint é alterado por este bundle.

## Próximos passos

- Integração de iluminação em cena exige WO própria com rendering e medição real.
- M04/M05/M06/M08 permanecem não admitidos; o contrato M03 e este planner são insumos.
