# NEX-M01-FINAL-REFERENCE-WO-001 | Fechamento do laboratório de referência M01

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0012` / `NEX-D-022`; instrução do Owner de 2026-11-15 para admitir rendering/runtime e finalizar os módulos base começando pelo M01.
**Base:** `main` `900d2b2d031a87048702625a1e98bc50905bc663`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (capturas nativas e medições no laboratório M01).
**Lock:** `.engineering/context-locks/NEX-M01-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M01 como laboratório de referência: aceitação S01 por cena/seed/backend, golden matrix S03 1920×1080 com A/A/A e A/B, orçamento S07 1080p aprovado, auditoria de licenças e gate final, permitindo fechar #21, #23, #27 e #6 após integração protegida.

## Escopo

- Capturas nativas 1920×1080: 18 golden PNGs e 9 runs de performance com validação canônica.
- `docs/benchmarks/m01/tools/build_golden_matrix.py` e `build_performance_budget.py`.
- `docs/benchmarks/m01/GOLDEN-MATRIX.md`, `FINAL-BUDGET.md`, `LICENSE-AUDIT.md`, `M01-FINAL-GATE.md`.
- Testes `tests/ci/test_m01_final.py`; enforcement dos builders no Fast Lane.
- `NEX-ADR-0012`, `NEX-D-022`, `AGENTS.md`, `SCOPE.md`, `CHECKPOINT.json`, WO/lock/evidência/delta.
- Fechamento de #21, #23, #27 e #6 após squash e checks pós-merge.

## Fora de escopo

- Jogo, gameplay, rede, servidor, MMORPG, cena de produção.
- Renderer/runtime de M02–M12, shaders customizados, compositor, GI, sombras/VFX reais.
- Assets de terceiros, cloud, serviços pagos.
- Claims generalizados de FPS/qualidade ou input-to-photon.
- M12/marca.

## DoD

- 18 golden PNGs 1920×1080, A/A byte-idêntico; A/B com métricas full + 5 regiões; 3 imagens de aceitação S01.
- 9 runs de performance validados; GPU p95 ≤ 1.0 ms, CPU p95 ≤ 2.0 ms, pacing p95 ≤ 16.67 ms, 1% low ≥ 60 FPS em todas as cenas.
- Budget 1080p `OWNER_APPROVED`; meta experimental 120 FPS medida no workload de referência.
- Auditoria de licenças com 0 assets de terceiros.
- Builders `--check` reproduzem JSON/Markdown; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issues #21, #23, #27 e #6 fechadas com comentário de evidência.

## STOP

- Base/HEAD divergente, captura não determinística, validação canônica falhando, budget não atingido sem explicação, check vermelho ou tentativa de claim generalizado → parar e registrar.
