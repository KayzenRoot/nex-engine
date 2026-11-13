# Evidence Bundle · NEX-SEC-MAIN-SONAR-C-001

**Issue:** #111 · **Risco:** STANDARD · **Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base:** `main` `47f95521821f71196ec54c8d74b20fa9c3a2a4a5`
**Branch:** `fix/nex-sec-main-sonar-c-001`

## 1. Investigação SonarCloud (dados reais)

Consultas anônimas à API pública do projeto (2026-11-13):

`GET /api/issues/search?componentKeys=KayzenRoot_nex-engine&branch=main&resolved=false&types=VULNERABILITY`

Resultado: **3 issues, todas MAJOR, todas em `tooling/godot/ci_build.py`**:

| Rule key | Severity | Line | Message |
|---|---|---|---|
| `pythonsecurity:S5144` | MAJOR | 129 | Server-Side Request Forgery via file content in `ci_build.download_verified()` |
| `pythonsecurity:S6350` | MAJOR | 313 | Command Argument Injection via file content in `ci_build.run_logged()` |
| `pythonsecurity:S6350` | MAJOR | 640 | Command Argument Injection via file content in `ci_build.windows_build()` |

`GET /api/measures/component?...&metricKeys=security_rating,new_security_rating,new_vulnerabilities`:

- `security_rating = 3.0` (C), `new_security_rating = 3.0` (C)
- `new_vulnerabilities = 3`, `vulnerabilities = 3`
- `security_hotspots = 0`, `security_review_rating = 1.0` (A)

Conclusão: o gate `C Security Rating on New Code` é causado exclusivamente pelas 3 vulnerabilidades acima. Não há hotspot pendente nem revisão de segurança pendente.

## 2. Causa raiz

O lock JSON (`.nex/toolchain/NEX-M00-WO-001-toolchain-lock.json`) é lido em `load_lock()` e seus valores fluem sem validação para:

- `urllib.request.Request(url, ...)` — `download_verified()` (linha 129);
- `subprocess.Popen(command, ...)` — `run_logged()` (linha 313);
- `subprocess.run([scons, "--help", *flags], ...)` — `windows_build()` (linha 640).

Ameaça: um lock adulterado (por alteração no repositório ou artefato intermediário) poderia direcionar download para host arbitrário ou injetar argumentos no build. Mesmo com SHA-256 pinado, a URL e os flags não eram validados contra um contrato de código.

## 3. Correção aplicada (sem supressão)

`tooling/godot/ci_build.py`:

- `TRUSTED_DOWNLOAD_URLS`: tupla constante com as 7 URLs exatas pinadas (Godot source/Windows/Linux, AccessKit, NIR, NIR license, SCons wheel).
- `trusted_download_url(url)`: retorna o **constante da tupla** correspondente; qualquer URL fora da allowlist levanta `IntegrityError` antes de qualquer requisição.
- `download_verified()` e `download_filename()` usam somente o valor allowlistado.
- `PINNED_WINDOWS_BUILD_FLAGS`: tupla constante; o lock deve ser idêntico (`lock_flags != PINNED_WINDOWS_BUILD_FLAGS` → `IntegrityError`); a lista usada no build vem do código.
- `PINNED_DEPENDENCY_DESTINATIONS`: mapeamento constante `AccessKit → accesskit`, `Mesa NIR → mesa`, validado contra `requiredFiles` do lock; paths usados no build vêm do código.
- Nome do wheel SCons e do arquivo Linux derivados de `download_filename()` (constante allowlistada), não de campos livres do lock.

Não houve alteração de regra, quality gate, workflow, dependência ou supressão de alerta.

## 4. Testes executados

Worktree byte-exato (`git -c core.autocrlf=false`), Python 3.13.15, suítes locais:

| Suíte | Resultado |
|---|---|
| `tests/m00` (inclui 6 testes novos de allowlist) | **23/23 PASS** |
| `tests/ci` | **106/106 PASS** |
| `tests/contracts` | **12/12 PASS** |
| `tests/telemetry` | **31/31 PASS** |
| **Total** | **172/172 PASS** |

Testes novos: allowlist de todas as URLs do lock; rejeição de `http://`, host não permitido, host lookalike, porta, `file://`, query, fragment, credenciais e vazio; rejeição antes de rede (`urlopen` não chamado); flags do lock idênticas às constantes; destinos de dependência idênticos ao mapeamento; rejeição de dependência sem mapeamento.

Observação local: no checkout Windows com `core.autocrlf=true`, 6 evidências JSON históricas aparecem com CRLF e falham asserts de SHA-256 no `tests/ci`; no worktree LF byte-exato e no CI Linux (autocrlf=false) a suíte passa 106/106. O defeito não pertence a esta correção.

## 5. Verificação exata de HEAD e pós-merge

- HEAD do PR e checks obrigatórios: registrados no PR e no comentário de auditoria solo (13/13).
- Pós-merge: repetir a consulta `/api/measures/component` na `main` e confirmar `security_rating = 1.0` (A) e `vulnerabilities = 0`; atualizar o checkpoint somente após essa verificação.
