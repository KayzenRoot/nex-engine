# Evidence Bundle · NEX-M09-CONTRACT-WO-001 (Preset pack contract v1)

**Status:** `CONTRACT_ONLY / NO_PRESET_APPLICATION / NO_RUNTIME_CLAIM / NOT_MODULE_ADMISSION`
**Issue:** #14 · **Base:** `8bf413f518e1cb4751fada9d313b2029711838b3` · **Code SHA:** `80ee24bd952103c6671a113bd755e2799231aa31`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `contracts/m09/preset_pack.v1.schema.json`: tiers low/medium/high/ultra/custom, blocos de rendering/lighting/performance/composition/feedback/accessibility, compatibilidade de contratos/Godot/hardware e proveniência.
- `contracts/m09/ownership.v1.json`: ownership prospectivo de `nex_modules/tools/**`.
- `docs/contracts/m09.md`: invariantes, validação, ownership e compatibilidade.
- `tests/contracts/test_m09_preset_pack_contract.py`: 16 testes.

## Invariantes verificados

- IDs de preset únicos; tiers padrão únicos (`custom` pode repetir).
- Todo preset tem ao menos um bloco de settings.
- Monotonicidade entre tiers consecutivos: `resolution_scale`, rank de `shadow_quality`, `shadow_atlas_size`, `target_fps`.
- `reduced_motion` exige `shake_scale <= 0.5` e `hit_stop_scale <= 1.0`.
- Versões de contrato únicas; `target_fps` é alvo, não medição; `fps` de topo rejeitado.
- Proveniência exige evidência quando medida.

## Verificação executada

```powershell
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
```

Resultado: **203 testes OK** (187 preexistentes + 16 novos).

## O que não foi feito / não é alegado

- Nenhum preset aplicado, `project.godot` alterado, UI de editor criada ou performance medida.
- Nenhum claim de FPS, qualidade ou compatibilidade real.
- M09 parent (#14) permanece `NOT_ADMITTED`; contratos M01–M08/M10–M12 inalterados.

## Rollback

Remover `contracts/m09/**`, `docs/contracts/m09.md`, o teste novo, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Resolver/aplicar presets exige WO própria; M09 parent e M12 parent permanecem não admitidos.
