# NEX-M09-CAMPAIGN-CLOSURE-WO-001 | Fechamento da campanha de resolução

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005); M09 é `BOUNDED_ADMITTED_EVIDENCE_PIPELINE` desde NEX-ADR-0006.
**Base:** `main` `b623bc429cc1770bfdb6a15cf8e8499b11dde14b`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** LOW (documentação de limitação de plataforma).
**Lock:** `.engineering/context-locks/NEX-M09-CAMPAIGN-CLOSURE-WO-001-EXECUTION.json`.

## Objetivo

Registrar formalmente a limitação de plataforma que encerra a campanha de resolução: uma tentativa de **3840×2160** foi clampada pelo desktop **2560×1080** para **2560×1009** e rejeitada como `INVALID`; a captura não foi commitada. Atualizar README e atlas para que futuros executores não repitam a tentativa sem um display/ambiente maior.

## Escopo

- `docs/benchmarks/m09/README.md`: nota de plataforma e encerramento da linha de resolução.
- `docs/benchmarks/m09/tools/build_measurement_atlas.py`: pergunta aberta atualizada.
- `docs/benchmarks/m09/measurement-atlas.v1.json` e `MEASUREMENT-ATLAS.md` regenerados.
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Commitar a captura 4K `INVALID` ou qualquer medição inválida.
- Alterar harness, cenas, presets, contratos, modelo, bundles M09 ou ruleset.
- Nova medição de performance/visual, animação ou câmera dinâmica.
- Novos parents, runtime, renderer, shaders, hub, `project.godot`.
- Claims de FPS, qualidade ou generalização.

## DoD

- README e atlas declaram a limitação de plataforma e a rejeição da captura 4K.
- Atlas regenerado; `--check` e testes do atlas verdes.
- Suítes CI/contratos/telemetria verdes; 24/24 builders.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, tentativa de commitar captura inválida, divergência do atlas ou check vermelho → parar e registrar.
