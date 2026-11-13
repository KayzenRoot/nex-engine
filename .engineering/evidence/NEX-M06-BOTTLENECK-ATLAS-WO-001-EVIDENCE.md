# Evidence Bundle · NEX-M06-BOTTLENECK-ATLAS-WO-001 (Atlas de gargalos S05)

**Status:** `EVIDENCE_DERIVED_ATLAS / SINGLE_SESSION / NO_NEW_MEASUREMENT / NO_BENCHMARK_CLAIM`
**Issue:** #11 · **Base:** `2a93668c1f72f1bb4e66ab5e35e037937c99c81f` · **Code SHA:** `99c9fcb4adc81a161ad5cb11f0010fdef9fe0b98`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `docs/benchmarks/m06/atlas.v1.json`: 15 runs, 13 células, referências baseline por contagem, deltas, classificação `pacing`/evidência/confiança, pressão de render e limitações.
- `docs/benchmarks/m06/ATLAS.md`: relatório humano com tabela de runs, referências baseline, observações e limitações.
- `docs/benchmarks/m06/tools/build_atlas.py`: builder stdlib determinístico com verificação de hashes, recomputação de agregados e `--check`.
- `docs/benchmarks/m06/README.md`: metodologia e uso.
- `tests/ci/test_m06_atlas.py`: 12 testes de estrutura e reprodutibilidade.

## Verificação executada

```powershell
python docs/benchmarks/m06/tools/build_atlas.py
python docs/benchmarks/m06/tools/build_atlas.py --check
python -m unittest tests.ci.test_m06_atlas -v
```

Resultado: **`ATLAS_WRITE_PASS: 15 runs, 32 hashes`**; **`ATLAS_CHECK_PASS`**; **12 testes OK**.

## Fatos derivados (não novos)

- 15/15 runs classificadas como `pacing`, evidência `measured`; vsync 60 Hz limita o frame no cenário sintético.
- GPU p95 máximo absoluto: **1.194 ms** em `combined-25`, ainda ~16.06 ms abaixo do pacing p95.
- Deltas GPU p95 vs baseline-25: lights +54.1%, shadows +154.1%, vfx +30.4%, combined +559.7%.
- Spread de GPU p50 nas 3 repetições baseline-25: **0.002 ms**.
- `render_pressure`: cpu em baseline/lights/vfx, balanced em shadows, gpu em combined.

## Integridade

- 32 arquivos de `SHA256SUMS.txt` verificados.
- Capturas de medição verificadas estritamente contra os blobs LF do Git; documentação/validação aceitam a variante CRLF original (limitação de line endings registrada).
- Cada JSON de validação S05 foi conferido contra os agregados recomputados (p50/p95/p99/mean, 1% low, duração).
- Nenhum run ausente ou extra; todos `COMPLETE`, mesmo `source_sha` `0b8388fa`.

## O que não foi feito / não é alegado

- Nenhuma captura, execução Godot, alteração de `nex_bench`/engine/CI ou medição nova.
- Nenhum benchmark, FPS, ganho, regressão ou generalização entre cenas/drivers/hardware/sessões.
- Allocation do renderer não é VRAM e não é comparada entre runs; 1% low é pacing de callbacks, não apresentação.
- M06 parent (#11) permanece `NOT_ADMITTED`.

## Rollback

Remover `docs/benchmarks/m06/**`, `tests/ci/test_m06_atlas.py`, este bundle, o delta e a WO/lock correspondentes. Nenhuma captura ou checkpoint é alterado.

## Próximos passos

- Capturas futuras com workload GPU-bound e múltiplas repetições podem alimentar o mesmo atlas via nova WO.
- M06 parent e submódulos (LOD/culling/streaming) permanecem não admitidos.
