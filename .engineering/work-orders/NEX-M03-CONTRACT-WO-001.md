# NEX-M03-CONTRACT-WO-001 | Contrato de iluminação cinematográfica v1

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; selecionado como habilitador independente após M07-S01.
**Base:** `main` `928ea7c14d253778a229e22133b982a0ee2167ef`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M03-CONTRACT-WO-001-EXECUTION.json` (20 fingerprints).

## Objetivo

Definir o contrato versionado de iluminação (ambiente, luzes, sombras, orçamento de sombra, disponibilidade de performance e proveniência), sem implementar M03 e sem alterar contratos existentes. Habilita futuras WOs de M03 com interface estável.

## Escopo

- `contracts/m03/lighting.v1.schema.json`, `contracts/m03/ownership.v1.json`.
- `docs/contracts/m03.md`.
- `tests/contracts/test_m03_lighting_contract.py`.

## Fora de escopo

- Implementação de luzes/sombras/GI, shaders, engine, CI, `project.godot`, M03 parent admission, M04–M12.
- Claims de qualidade/performance.

## DoD

- Contrato válido, ownership prospectivo, testes verdes, checks verdes, squash protegido; delta de checkpoint proposto.

## STOP

- Divergência de contrato/check ou necessidade de implementação → parar/escalar.
