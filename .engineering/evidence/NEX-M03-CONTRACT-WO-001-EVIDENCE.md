# Evidence Bundle · NEX-M03-CONTRACT-WO-001 (Lighting contract v1)

**Status:** `CONTRACT_ONLY / NO_LIGHTING_IMPLEMENTATION / NO_PERFORMANCE_CLAIM / NOT_MODULE_ADMISSION`
**Issue:** #8 · **Base:** `928ea7c14d253778a229e22133b982a0ee2167ef` · **Code SHA:** `38e1d4cb52f8ca8801fc35492ca9afe0d565e419`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `contracts/m03/lighting.v1.schema.json`: observação de iluminação versionada (`lighting.v1`) com ambiente (ambient source/cor/energia, tonemap, glow, fog, GI), 1–128 luzes (`directional`/`omni`/`spot`, cor, energia, sombra, bias/softness, cull mask, range/spot angle/cascades condicionais), orçamento de sombra, métricas de performance com disponibilidade explícita e proveniência (SHAs, Godot, hardware, capture mode, status, evidence URI).
- `contracts/m03/ownership.v1.json`: ownership prospectivo `CONTRACT_ONLY_PROSPECTIVE_OWNERSHIP_NOT_MODULE_ADMISSION`, writer `integration-steward`, paths futuros de `nex_modules/lighting/**` sem admissão implícita.
- `docs/contracts/m03.md`: propósito, invariantes, validação, ownership e compatibilidade.
- `tests/contracts/test_m03_lighting_contract.py`: 16 testes (schema standalone/versionado, fixture válida, ausência de campo obrigatório, rejeição de FPS, semântica MEASURED/UNAVAILABLE, proibição de métrica MEASURED sob UNAVAILABLE global, duplicidade de `light_id`, coerência tipo↔campo, orçamento de sombra/cascades/caster sem energia, evidência obrigatória quando MEASURED, SHA/observation_id inválidos, 15 perturbações negativas, ownership normalizado/disjunto).

## Verificação executada

```powershell
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
```

Resultado: **57 testes OK** (41 preexistentes + 16 novos), 0 falhas.

Os testes usam o checker stdlib limitado do repositório, com expansão de `$ref` via `_resolve_refs` compartilhado; não é um validador Draft 2020-12 completo.

## O que não foi feito / não é alegado

- Nenhuma luz, sombra, GI, shader, cena ou renderer implementado; nenhum arquivo em `nex_modules/**` ou `nex_bench/**` alterado.
- Performance/qualidade visual/frame-time: `INCONCLUSIVE_NOT_RUN`; o schema apenas representa métricas quando medidas por provedor real.
- M03 parent (#8) permanece `NOT_ADMITTED`; o contrato habilita WOs futuras, não as autoriza.
- Nenhum contrato M01/M02/M07 alterado; nenhum arquivo de CI ou `project.godot` tocado.

## Rollback

Remover `contracts/m03/**`, `docs/contracts/m03.md`, `tests/contracts/test_m03_lighting_contract.py`, este bundle, o delta e a WO/lock correspondentes. Nenhum estado de engine ou checkpoint é alterado.

## Próximos passos

- WOs de M03 exigem admissão própria com Context Lock e implementação separada.
- M04/M05/M06/M08 permanecem não admitidos; contratos futuros seguem o mesmo padrão.
