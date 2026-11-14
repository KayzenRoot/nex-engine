# Evidence Bundle · NEX-M09-RES-1440-WO-001

**Status:** `MEASURED_EVIDENCE / SINGLE_SESSION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M09 #14 · **M03 context:** #8 · **Base:** `39633b347784e66526c60be6c655d007d86f16cd`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Sessão de **6 capturas** em `arena_combat`, 100 proxies, 2560×1440, A/B/A (low/high ×3), 2 s warmup e 30 s observação, VSync off, `max_fps 240`.
- Evidence bundle `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling-1440/`: 6 capturas, 6 validações PASS, manifesto, fatos, análise e SHA-256 (15 arquivos).
- Núcleo compartilhado `arena_resolution.py`; refactor de `build_interaction_200_720.py` com saída byte-idêntica.
- Builder `build_res_scaling_1440.py`; relatório `res-scaling-1440.v1.json` + `RES-SCALING-1440-REPORT.md`.
- Atlas M09 atualizado para **12 bundles, 156 capturas de performance, 66 imagens, 414 arquivos e 12 source SHAs**.
- `tests/ci/test_res_scaling_1440.py` (6 testes); **23 comandos `--check` / 20 arquivos**.
- WO/lock/evidência/delta correspondentes.

## Resultado

- GPU p95 mediano: **0.206 ms** (`ab-low`) e **1.547 ms** (`ab-high`); high/low **+651.0%**.
- Deltas de resolução: 1920→2560 **+32.1%/+87.3%**; 960→2560 **+114.6%/+388.0%**.
- Modelo M03: `ab-high` previsto 0.460 ms vs medido 1.547 ms (**−70.3%**, fora de 2%); `ab-low` previsto 0.379 ms vs 0.206 ms (**+84.0%**, fora).
- Conclusão: a dominância de resolução continua em 2560×1440 e o acerto de 2% do `ab-high` não sobrevive a essa resolução; ele é específico de 1280×720.
- Uma run `ab-low` tem outlier isolado de 1% low (38.9 fps), reportado; medianas usadas.

## Verificação

- 6/6 capturas `COMPLETE` e `PASS`, proxy 100 e viewport 2560×1440.
- `--check` do novo builder PASS; `build_interaction_200_720.py --check` PASS após o refactor.
- 23/23 builders PASS em worktree LF limpo.
- Suítes: CI **514**, contratos **203**, telemetria **31** — OK.
- Nenhum harness, cena, preset, contrato, coeficiente, snapshot, renderer, shader ou `project.godot` alterado.

## O que não foi feito / não é alegado

- Nenhuma generalização cross-device, cross-driver ou cross-sessão; uma sessão em RTX 5050.
- A janela 2560×1440 é maior que o desktop 2560×1080; o viewport é capturado off-screen.
- Animação, câmera dinâmica, efeitos temporais e resoluções acima de 2560×1440 não cobertos.
- Nenhum parent novo admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Remover o evidence bundle, builders/core, relatórios, atualização do atlas, testes, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
