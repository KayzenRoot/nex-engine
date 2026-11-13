# Evidence Bundle · NEX-M04-M05-CONTRACTS-WO-001 (Material + SpellFX contracts v1)

**Status:** `CONTRACT_ONLY / NO_IMPLEMENTATION / NO_VISUAL_CLAIM / NOT_MODULE_ADMISSION`
**Issues:** #9 (M04), #10 (M05) · **Base:** `11d8e61579680166bb36a645502d97e60b23a832` · **Code SHA:** `e1d89adeb6c86507032571987075b75c6ec64b70`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `contracts/m04/material.v1.schema.json`: observação PBR versionada com identidade de material/shader, superfície (albedo, metallic, roughness, emissão, normal/occlusion), alpha/cull, variante de qualidade, texturas com slot/SHA-256/dimensões/mips/sRGB, orçamento de textura, performance com disponibilidade explícita e proveniência.
- `contracts/m04/ownership.v1.json`: ownership prospectivo `CONTRACT_ONLY_PROSPECTIVE_OWNERSHIP_NOT_MODULE_ADMISSION`.
- `contracts/m05/spellfx.v1.schema.json`: catálogo de magias com elemento, fases cast/travel/impact/linger, emissores (particles/trail/beam/decal/light), gameplay authority, decal policy, orçamento FX, performance e proveniência.
- `contracts/m05/ownership.v1.json`: ownership prospectivo de `nex_modules/vfx/**`.
- `docs/contracts/m04.md` e `docs/contracts/m05.md`: invariantes, validação, ownership e compatibilidade.
- `tests/contracts/_contract_support.py`: helpers compartilhados (schema com `$ref`, performance/proveniência, orçamento de textura).
- `tests/contracts/test_m04_material_contract.py` (16 testes) e `test_m05_spellfx_contract.py` (20 testes).

## Invariantes verificados

- Material: ids únicos, slots únicos por material, `mask` exige `alpha_cutoff` e `opaque` o proíbe, contagem/bytes estimados de textura dentro do orçamento, SHA-256 lowercase, proveniência com evidência quando `MEASURED`.
- SpellFX: ids de magia/fase/emissor únicos, fase `impact` obrigatória, `damage_owner`/`hit_detection` sempre `gameplay`, coerência `light`↔`light_bridge`, totais de emissores/partículas/GPU/decals dentro do orçamento, duração total ≤ 60000 ms, `decal_policy` dentro do budget.
- Ambos rejeitam FPS, campos desconhecidos e métricas `MEASURED` sob `UNAVAILABLE` global.

## Verificação executada

```powershell
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
```

Resultado: **93 testes OK** (57 preexistentes + 36 novos), 0 falhas.

## O que não foi feito / não é alegado

- Nenhum material, shader, textura, partícula, emissor, luz ou decal implementado; nenhum arquivo em `nex_modules/**`, `nex_bench/**` ou CI alterado.
- Nenhum claim visual, de FPS, frame-time ou VRAM.
- M04 (#9) e M05 (#10) permanecem `NOT_ADMITTED`; os contratos habilitam WOs futuras.
- Contratos M01/M02/M03/M07 não foram alterados.

## Rollback

Remover `contracts/m04/**`, `contracts/m05/**`, `docs/contracts/m04.md`, `docs/contracts/m05.md`, `tests/contracts/_contract_support.py`, os dois testes novos, este bundle, o delta e a WO/lock correspondentes. Nenhum estado de engine ou checkpoint é alterado.

## Próximos passos

- WOs de M04/M05 exigem admissão própria e implementação separada.
- M06/M08/M12 permanecem não admitidos.
