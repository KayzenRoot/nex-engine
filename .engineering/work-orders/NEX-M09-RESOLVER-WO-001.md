# NEX-M09-RESOLVER-WO-001 | Resolvedor de preset packs

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente que consome `preset_pack.v1`.
**Base:** `main` `ec7048ff0c52671d2fb4d6b8e84aaf15ac9fef5d`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M09-RESOLVER-WO-001-EXECUTION.json` (29 fingerprints).

## Objetivo

Implementar um resolvedor determinístico de preset packs: carregar/validar um `preset_pack.v1`, checar compatibilidade de hardware/Godot/contratos, resolver por tier ou preset id, aplicar overrides com merge profundo e validar reduced motion. Nenhum preset é aplicado em engine/`project.godot`.

## Escopo

- `nex_modules/tools/preset_resolver/`: projeto Godot autocontido (`preset_resolver.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, log headless).
- `tests/ci/test_preset_resolver.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Aplicar presets, alterar `project.godot`/engine/CI, criar UI de editor.
- M09 parent admission.
- Claims de FPS, qualidade ou compatibilidade medida.

## DoD

- Resolução, merge, compatibilidade e erros determinísticos, alinhados a `preset_pack.v1`.
- Smoke headless verde, testes estruturais verdes, suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência entre resolvedor e contrato, check vermelho ou necessidade de aplicação em runtime → parar e registrar.
