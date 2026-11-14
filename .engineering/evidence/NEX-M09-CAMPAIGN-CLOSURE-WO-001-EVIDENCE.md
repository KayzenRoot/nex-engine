# Evidence Bundle · NEX-M09-CAMPAIGN-CLOSURE-WO-001

**Status:** `PLATFORM_LIMITATION_RECORDED / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M09 #14 · **Base:** `b623bc429cc1770bfdb6a15cf8e8499b11dde14b`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** LOW

## Entregue

- `docs/benchmarks/m09/README.md`: nota de que uma tentativa 3840×2160 foi clampada pelo desktop 2560×1080 para 2560×1009 e rejeitada como `INVALID`; resoluções acima de 2560×1440 exigem display/ambiente maior.
- `build_measurement_atlas.py`: pergunta aberta atualizada com a limitação de plataforma.
- `measurement-atlas.v1.json` e `MEASUREMENT-ATLAS.md` regenerados.
- WO/lock/evidência/delta.

## Resultado

- Nenhuma captura inválida foi commitada.
- A campanha de resolução está formalmente encerrada em 2560×1440 neste ambiente.
- O atlas permanece com 13 bundles / 84 imagens / 435 arquivos.

## Verificação

- `build_measurement_atlas.py --check` e `test_measurement_atlas.py` verdes.
- Suítes CI/contratos/telemetria e 24/24 builders verdes.
- Nenhum harness, cena, preset, contrato, modelo, bundle M09 ou ruleset alterado.

## O que não foi feito / não é alegado

- Nenhuma medição 4K válida; nenhuma captura inválida commitada.
- Nenhuma generalização cross-device/cross-sessão.
- Nenhum parent novo admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter README, atlas builder/artefatos, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
