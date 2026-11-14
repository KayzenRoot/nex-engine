# NEX-CP-CORRECTION-001 | Correção de contadores do checkpoint

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** correção de coerência documental sob NEX-ADR-0005; sem nova medição.
**Base:** `main` `599746391bad6d4acf6fc689f01f0d5cc7e309a5`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** LOW.
**Lock:** `.engineering/context-locks/NEX-CP-CORRECTION-001-EXECUTION.json`.

## Objetivo

Corrigir dois contadores do checkpoint após a autoinclusão do bloco `provenanceIndex`:
- `provenanceIndex.entries` 57 → **58** e `maxPr` 241 → **243** (o índice agora inclui o próprio bloco).
- `ciBuilderCheckEnforcement.builderCommands` 24 → **25** e `builderFiles` 21 → **22** (o builder cross-module entrou no workflow).
- Atualizar a seção do checkpoint de 57/112–241 para 58/112–243.

## Escopo

- `.engineering/CHECKPOINT.json` e `.engineering/CHECKPOINT.md`.
- WO/lock/evidência/delta.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Alterar o índice de proveniência, blocos de admissão, medições, harness, contratos, modelo ou ruleset.
- Nova medição, captura ou renderização.
- Novos parents ou issues `PLANNING_ONLY`.

## DoD

- Contadores do checkpoint iguais aos artefatos: 58 entradas, PR máximo 243, 25 comandos, 22 arquivos.
- `build_provenance_index.py --check` e teste de proveniência verdes.
- Suítes verdes; PR protegida e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, divergência do índice ou check vermelho → parar e registrar.
