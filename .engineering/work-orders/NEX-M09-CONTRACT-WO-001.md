# NEX-M09-CONTRACT-WO-001 | Contrato de preset packs v1

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente para ferramentas de editor/presets.
**Base:** `main` `8bf413f518e1cb4751fada9d313b2029711838b3`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M09-CONTRACT-WO-001-EXECUTION.json` (28 fingerprints).

## Objetivo

Definir `preset_pack.v1` para packs de presets de editor/qualidade: tiers low→ultra/custom, blocos de render, iluminação, performance, composição 2.5D, feedback e acessibilidade, compatibilidade de contratos/hardware e proveniência. Nenhum preset é aplicado ou validado em runtime.

## Escopo

- `contracts/m09/preset_pack.v1.schema.json`, `contracts/m09/ownership.v1.json`.
- `docs/contracts/m09.md`.
- `tests/contracts/test_m09_preset_pack_contract.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Aplicar presets, alterar `project.godot`/engine/CI, gerar UI de editor.
- M09 parent admission.
- Claims de FPS, qualidade ou compatibilidade medida.

## DoD

- Contrato válido com invariantes de tier/monotonicidade/acessibilidade/compatibilidade.
- Testes verdes e suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência de contrato, check vermelho ou necessidade de aplicação em runtime → parar e registrar.
