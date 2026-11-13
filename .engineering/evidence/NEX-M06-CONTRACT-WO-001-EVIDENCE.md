# Evidence Bundle · NEX-M06-CONTRACT-WO-001 (Performance contract v1)

**Status:** `CONTRACT_ONLY / NO_MEASUREMENT / NO_BENCHMARK_CLAIM / NOT_MODULE_ADMISSION`
**Issue:** #11 · **Base:** `beab4ac0eab6b57455cde57ff6627b74b46a4cd7` · **Code SHA:** `78af311cdb0e04f94f23f1c1a3d5e33e991fbad8`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `contracts/m06/performance.v1.schema.json`: observação versionada com workload (cena, proxies, effect mode, resolução, vsync, max_fps), frame interval, timings GPU/CPU/pacing, recursos (draw calls, objetos, alocação, VRAM), classificação de gargalo com evidência/confiança/razão, comparação opcional e proveniência.
- `contracts/m06/ownership.v1.json`: ownership prospectivo de atlas/LOD/culling/streaming/framepacer.
- `docs/contracts/m06.md`: invariantes, validação, ownership e compatibilidade.
- `tests/contracts/test_m06_performance_contract.py`: 17 testes.

## Invariantes verificados

- `MEASURED` exige valor; `UNAVAILABLE` exige razão e proíbe valor; zero é medição válida.
- Classificação `gpu`/`cpu`/`pacing`/`memory` exige a métrica correspondente `MEASURED` quando a evidência não é `unavailable`.
- `insufficient_data` proíbe qualquer métrica `MEASURED`; evidência `unavailable` só vale para `unknown`/`insufficient_data`.
- Comparação opcional limitada a deltas `[-10000, 10000]`.
- Proveniência exige evidência quando `MEASURED`; SHAs lowercase.
- FPS e campos desconhecidos são rejeitados.

## Verificação executada

```powershell
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
```

Resultado: **110 testes OK** (93 preexistentes + 17 novos), 0 falhas.

## O que não foi feito / não é alegado

- Nenhuma captura, medição, benchmark ou alteração em `nex_bench`/engine/CI.
- Nenhuma classificação de gargalo real é afirmada; o contrato apenas valida documentos.
- Nenhum claim de FPS, ganho ou regressão.
- M06 parent (#11) permanece `NOT_ADMITTED`.
- Contratos M01–M05/M07 não foram alterados.

## Rollback

Remover `contracts/m06/**`, `docs/contracts/m06.md`, `tests/contracts/test_m06_performance_contract.py`, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Uso real do contrato exige captura com provedor de GPU/pacing e WO própria.
- M08/M12 permanecem não admitidos.
