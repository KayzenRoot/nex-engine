# NEX-QA-AUDIT-WO-001 · Relatório de auditoria de robustez

**Issue:** #20 (NEX-QA-PROP-001) · **Onda:** NEX-WAVE-001 frente 3
**Modo:** ADMIN_SOLO / `NOT_INDEPENDENT` (NEX-ADR-0004 / NEX-D-014)
**Base:** `main` `a743032` · **Data:** 2026-11-13
**Harness:** `qa/bug-reports/NEX-QA-AUDIT-WO-001/harness/fuzz_validators.py` (determinístico, stdlib, sem rede)

## Escopo e método

Corpus fixo de 68 casos aplicado a quatro fronteiras de entrada não confiável:

1. `nex_bench/gpu_profile/validate_gpu_profile.py` — JSON v2 de perfis GPU (17 casos).
2. `nex_bench/telemetry/framepulse.py` — JSON de telemetria sintética (16 casos).
3. `nex_bench/visual_truth/compare.py` — parser PNG e limites de imagem (14 casos).
4. `tooling/godot/ci_build.py` — allowlist de URLs e nomes de download (21 casos).

Cada caso declara expectativa `accept`/`reject`; o harness classifica exceções controladas da família documentada (`ValueError`/`ProfileError`/`FramePulseError`/`ImageFormatError`/`IntegrityError`) e registra exceções inesperadas ou aceitações indevidas. O resultado bruto está em `FUZZ-RESULTS.json`.

## Resultado

| Alvo | Casos | Rejeições controladas | Exceções inesperadas | Aceitações indevidas |
|---|---:|---:|---:|---:|
| `validate_gpu_profile` | 17 | 17 | 0 | 0 |
| `framepulse.analyze_json` | 16 | 15 | **1** | 0 |
| `visual_truth.compare.read_png` | 14 | 13 (1 válido aceito) | 0 | 0 |
| `ci_build` allowlist | 21 | 14 (7 válidos aceitos) | 0 | 0 |
| **Total** | **68** | — | **1** | **0** |

## Achado QA-FINDING-001 (LOW)

**Título:** `framepulse.analyze_json` propaga `RecursionError` em JSON profundamente aninhado.

- **Entrada:** string com 10.000 colchetes de abertura (`"[" * 10000`).
- **Esperado:** rejeição controlada (`FramePulseError`), como nos demais JSON inválidos.
- **Observado:** `RecursionError` não capturado (traceback) — `analyze_json` captura `TypeError`, `ValueError` e `OverflowError`, mas não `RecursionError`.
- **Contraste:** `validate_gpu_profile.validate_payload` captura `(ValueError, RecursionError)` e converte em `ProfileError`; o comportamento é inconsistente entre validadores.
- **Impacto:** baixo (ferramenta local; entrada não confiável pode causar falha não controlada do processo chamador). Não há serviço remoto nem bypass de validação.
- **Correção proposta (não aplicada — fora do escopo de QA):** incluir `RecursionError` no `except` de `analyze_json` e levantar `FramePulseError("invalid JSON telemetry: ...")`; teste de regressão correspondente.
- **Status:** `OPEN` — requer Correction WO próprio. O teste em `tests/ci/test_qa_audit_regressions.py` documenta o comportamento atual (aceita `FramePulseError` ou `RecursionError`) e deve ser endurecido para exigir `FramePulseError` após a correção.

## Comportamentos verificados (sem defeito)

- **GPU validator:** rejeita JSON vazio, `null`, `[]`, `{}`, chaves duplicadas, `NaN`/`Infinity`, inteiros gigantes, truncamento, UTF-8 inválido e aninhamento profundo; impõe limite de 8 MB. Nenhuma aceitação indevida.
- **PNG parser:** rejeita assinatura inválida, cabeçalho truncado, CRC corrompido, dimensões zero/acima do limite, IHDR duplicado, IEND não vazio, dados após IEND, filtro de linha inválido, tipo de cor não suportado e fluxo zlib truncado; dimensões e bytes comprimidos são limitados antes da descompressão.
- **Allowlist de build:** as 7 URLs pinadas são aceitas; 14 variantes maliciosas (http, host lookalike, userinfo, porta, query, fragment, case alternado, ponto final, encoding `%2e`, `file://`, espaço final, credenciais) são rejeitadas com `IntegrityError`.

## Metodologia e transparência

Dois falsos positivos foram identificados e corrigidos durante a triagem, antes de qualquer conclusão: (a) `IntegrityError` herda de `RuntimeError`, não de `ValueError`, e foi reclassificado como rejeição controlada; (b) o fixture "PNG válido" inicial não incluía o byte de filtro por linha e era de fato malformado. Nenhum produto foi alterado para fazer o harness passar.

## Limites

Sem execução de Godot, GPU, rede ou campanha de fuzzing estatístico; corpus determinístico de engenharia de robustez. Não substitui revisão semântica da lógica de negócio.

## Reprodução

```powershell
python qa/bug-reports/NEX-QA-AUDIT-WO-001/harness/fuzz_validators.py
```

Saída esperada: 68 casos, 0 aceitações indevidas, 1 exceção inesperada (QA-FINDING-001).
