# Evidence Bundle · NEX-M06-ATLAS-REPAIR-WO-001 (Sonar + bytecode)

**Status:** `REPAIR_EVIDENCE / NO_BEHAVIOR_CHANGE / ADMIN_SOLO_NOT_INDEPENDENT`
**Issue:** #11 · **Base:** `aee4c15cf5bd912ea31fa36731cca55671776080` · **Code SHA:** `0b7eda722e2b1b465217ef1a27f5e6830d9e1262`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `docs/benchmarks/m06/tools/build_atlas.py`:
  - S9454 (6): blocos de `append` consecutivos convertidos em listas + `extend`.
  - S6353 (6): classes `[0-9]` substituídas por `\d`.
  - S3776 (1): `verify_bundle` reduzido; verificação por arquivo extraída para `_verify_entry`.
  - S7500 (1): hook `parse_constant` nomeado (`_reject_non_finite`) no lugar do gerador.
- `docs/benchmarks/m06/tools/.gitignore`: ignora `__pycache__/` e `*.pyc`.
- Remoção de `docs/benchmarks/m06/tools/__pycache__/build_atlas.cpython-313.pyc` (rastreado acidentalmente na PR #159).

## Verificação executada

```powershell
python docs/benchmarks/m06/tools/build_atlas.py --check
python -m unittest tests.ci.test_m06_atlas -v
```

Resultado: **`ATLAS_CHECK_PASS: 15 runs, 32 hashes`**; **12 testes OK**.

- `atlas.v1.json` e `ATLAS.md` não foram alterados neste commit (byte-idênticos).
- Hashes do bundle continuam verificados; capturas de medição seguem estritas contra blobs LF.
- Nenhum teste foi alterado.
- Nenhum arquivo `.pyc` permanece rastreado (`git ls-files` vazio para `__pycache__`/`*.pyc`).

## Achados Sonar endereçados

| Regra | Antes | Depois |
|---|---:|---:|
| `python:S9454` | 6 | 0 |
| `python:S6353` | 6 | 0 |
| `python:S3776` (builder) | 1 | 0 |
| `python:S7500` | 1 | 0 |

A confirmação final é feita pela análise SonarCloud da PR e da main pós-merge.

## O que NÃO muda

- Nenhum atlas, MD, teste, contrato, captura, engine, CI ou `project.godot` alterado.
- Nenhum claim de performance, benchmark ou generalização.
- M06 parent (#11) permanece `NOT_ADMITTED`.

## Rollback

Reverter este commit restaura o builder anterior e o `.pyc`; não há impacto em dados ou artefatos.
