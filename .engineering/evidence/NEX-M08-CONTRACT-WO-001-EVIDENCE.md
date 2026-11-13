# Evidence Bundle · NEX-M08-CONTRACT-WO-001 (2.5D composition contract v1)

**Status:** `CONTRACT_ONLY / NO_2.5D_IMPLEMENTATION / NO_VISUAL_CLAIM / NOT_MODULE_ADMISSION`
**Issue:** #13 · **Base:** `4f692369f7a94378c3bee431fa67fe37fca8c324` · **Code SHA:** `53c38b35d8f913b703deb3817bdde63ec501f7aa`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `contracts/m08/composition.v1.schema.json`: observação 2.5D versionada com referência ao plano 3D, stack de camadas (background/gameplay/foreground/hud), parallax, blend, alpha, `depth_override_m`, política de profundidade, alpha guard, HUD/overlay safety, entidades críticas, performance e proveniência.
- `contracts/m08/ownership.v1.json`: ownership prospectivo de `nex_modules/render2_5d/**`.
- `docs/contracts/m08.md`: invariantes, validação, ownership e compatibilidade.
- `tests/contracts/test_m08_composition_contract.py`: 20 testes.

## Invariantes verificados

- IDs de camada/entidade únicos; HUD referenciado deve existir e ser `role: hud`.
- HUD nunca declara `depth_override_m`; `depth_policy: inherit_3d` proíbe override em qualquer camada.
- Entidade com `must_remain_visible: true` exige `critical_guard: true`.
- Overlay que pode cobrir gameplay exige `conflict_policy: report` (nunca silencioso).
- `plan_schema: none` exige contagens/riscos zerados; plano real exige `plan_sha256` lowercase.
- Performance `MEASURED`/`UNAVAILABLE` coerente; proveniência exige evidência quando medida.
- FPS e campos desconhecidos rejeitados.

## Verificação executada

```powershell
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
```

Resultado: **130 testes OK** (110 preexistentes + 20 novos).

## O que não foi feito / não é alegado

- Nenhuma camada, viewport, shader, cena, 2.5D ou rendering implementado.
- Nenhum claim visual, de FPS, frame-time ou VRAM.
- M08 parent (#13) permanece `NOT_ADMITTED`; contratos M01–M07/M06 inalterados.
- O rascunho DepthWeave permanece como origem documental, não como implementação.

## Rollback

Remover `contracts/m08/**`, `docs/contracts/m08.md`, o teste novo, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Protótipo de planejador de composição 2.5D exige WO própria, consumindo este contrato.
- M08 parent e integração em cena permanecem não admitidos.
