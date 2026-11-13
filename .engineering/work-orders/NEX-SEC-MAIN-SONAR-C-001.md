# NEX-SEC-MAIN-SONAR-C-001 | Correção de Security Rating C na main

**Status:** `ADMITTED_BY_ISSUE_111 / EXECUTION_ADMIN_SOLO / NOT_INDEPENDENT`
**Issue:** #111 — NEX-SEC-MAIN-SONAR-C-001
**Risco:** STANDARD (tooling de build; não altera runtime do engine)
**Modo:** ADMIN_SOLO conforme NEX-ADR-0004 / NEX-D-014; auditoria identificada como `NOT_INDEPENDENT`.
**Data:** 2026-11-13

## Escopo exato (somente estes arquivos)

- `tooling/godot/ci_build.py`
- `tests/m00/test_ci_build.py`
- `.engineering/work-orders/NEX-SEC-MAIN-SONAR-C-001.md` (este arquivo)
- `.engineering/evidence/NEX-SEC-MAIN-SONAR-C-001-EVIDENCE.md`

**Fora de escopo:** regras do Sonar, quality gate, ruleset, workflow CI, supressões/annotations, mudanças de dependência, código do engine.

## Causa raiz (confirmada por API SonarCloud)

Três vulnerabilidades MAJOR em `tooling/godot/ci_build.py`, todas com fluxo de taint a partir do lock JSON:

1. `pythonsecurity:S5144` (linha 129) — SSRF: URL de download lida do lock chega a `urllib.request.Request`.
2. `pythonsecurity:S6350` (linha 313) — command argument injection: comando de build derivado do lock chega a `subprocess.Popen` em `run_logged`.
3. `pythonsecurity:S6350` (linha 640) — command argument injection: flags derivadas do lock chegam a `subprocess.run` (`scons --help`).

O rating Security C (3.0) deriva dessas 3 vulnerabilidades MAJOR em New Code.

## Correção (sem supressão)

- **URLs:** allowlist reviewada de strings exatas (`TRUSTED_DOWNLOAD_URLS`); `trusted_download_url()` devolve o **constante** da allowlist e rejeita qualquer outro valor antes de qualquer rede. `download_verified()` e `download_filename()` usam somente o valor validado.
- **Flags de build:** `PINNED_WINDOWS_BUILD_FLAGS` constante; o lock é comparado e deve ser idêntico; a lista usada vem do código, não do lock.
- **Destinos de dependência:** `PINNED_DEPENDENCY_DESTINATIONS` constante com verificação de igualdade contra o lock; nomes usados nos paths vêm do código.
- **Arquivos de download:** nome derivado via `download_filename()` da URL allowlistada (constante), não de campos livres do lock.
- Nenhum alerta suprimido, nenhuma regra/quality gate alterada, nenhum check desativado.

## Testes e DoD

- 6 testes novos em `tests/m00/test_ci_build.py`: allowlist de URLs, rejeição de URLs maliciosas, rejeição antes da rede, flags pinadas, destinos pinados, rejeição de dependência não mapeada.
- Suítes: `tests/m00` 23/23; `tests/ci` 106/106; `tests/contracts` 12/12; `tests/telemetry` 31/31 (172/172, worktree LF byte-exato).
- DoD: (a) 3 vulnerabilidades resolvidas na análise Sonar do PR sem novos issues; (b) 13/13 checks no HEAD exato; (c) pós-merge, Security Rating A na main; (d) checkpoint atualizado somente após verificação.

## STOP

- Sonar do PR continuar apontando S5144/S6350 no código alterado → iterar; **sem merge**.
- Qualquer check obrigatório falhar → **sem merge**.
- Necessidade de mudar regra/quality gate/suprimir → **parar** e escalar ao Owner (fora do escopo).
