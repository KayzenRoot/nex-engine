# NEX M01 Benchmark Audit Pack

**Status:** `FROZEN_PROPOSED` · auditoria `ADMIN_SOLO / NOT_INDEPENDENT` · base `871fd1b`.
Este pacote consolida as evidências S01–S06 em um baseline auditável. **Não** declara conclusão do engine, metas de FPS atingidas ou admissão de módulos.

## Conteúdo

- `manifest.json` — índice verificável (caminho + SHA-256) de todos os artefatos e matrizes.
- `BASELINE.md` — o que está congelado e o que não está.
- `PERFORMANCE-BUDGET.md` / `budget.v1.json` — tetos propostos e metas aspiracionais.
- `RISKS.md` / `DEVIATIONS.md` / `CI_LINKS.md`.
- `research.md` — insumos do S06.
- `runs/`, `visual/`, `stress/` — índices por família de evidência.
- `tools/build_manifest.py` — recalcula e verifica todos os digests.

## Verificação

```powershell
python docs/benchmarks/m01/tools/build_manifest.py --check
python -m unittest discover -s tests/ci -p "test_m01_baseline_audit.py" -v
```

Qualquer divergência de byte falha a verificação. O pacote não duplica arquivos grandes; referencia os originais no repositório.
