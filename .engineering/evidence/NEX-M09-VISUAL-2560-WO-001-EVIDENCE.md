# Evidence Bundle · NEX-M09-VISUAL-2560-WO-001

**Status:** `VISUAL_EVIDENCE / SINGLE_SESSION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parents:** M09 #14 · M01 #6 · **Base:** `4f739cd6808677cd7e3780a8bedb295da55e046d`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Sessão visual de **18 PNGs** em `corridor_static`, `arena_combat` e `dense_city`, 2560×1440, 2 presets × 3 repetições.
- Evidence bundle `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-2560/`: 18 PNGs, manifesto, fatos, análise e SHA-256 (21 arquivos).
- Núcleo compartilhado `visual_truth.py`; refactor de `build_m01_visual_1920.py` com saída byte-idêntica.
- Builder `build_m01_visual_2560.py`; relatório `m01-visual-2560.v1.json` + `M01-VISUAL-2560-REPORT.md`.
- Atlas M09 atualizado para **13 bundles, 84 imagens, 435 arquivos e 13 source SHAs**.
- `tests/ci/test_m01_visual_2560.py` (5 testes); **24 comandos `--check` / 21 arquivos**.
- WO/lock/evidência/delta correspondentes.

## Resultado

- A/A byte-idêntico por SHA em todas as três repetições de cada cena/preset.
- A/B changed pixels: **2.996%** (corridor), **3.074%** (arena), **1.031%** (city); mean abs **0.3694/0.3863/0.1524**.
- Comparação com 1920×1080: Δ mean abs **−11.4%/−8.4%/−14.6%**, continuando a tendência de queda com a resolução.
- Uma captura inicial corridor/high foi clipada para 2560×1009 e recapturada; a imagem commitada é 2560×1440.

## Verificação

- 18/18 PNGs 2560×1440, 3 canais, hashes do manifesto conferidos.
- `--check` do novo builder PASS; `build_m01_visual_1920.py --check` PASS após o refactor.
- 24/24 builders PASS em worktree LF limpo.
- Suítes: CI **520**, contratos **203**, telemetria **31** — OK.
- Nenhum harness, cena, preset, contrato, renderer, shader ou `project.godot` alterado.

## O que não foi feito / não é alegado

- Nenhuma medição de performance nova; nenhum claim de FPS ou qualidade.
- Nenhuma generalização cross-device, cross-driver ou cross-sessão; uma sessão em RTX 5050.
- Animação, câmera dinâmica, efeitos temporais e resoluções acima de 2560×1440 não cobertos.
- Nenhum parent novo admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Remover o evidence bundle, builders/core, relatórios, atualização do atlas, testes, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
