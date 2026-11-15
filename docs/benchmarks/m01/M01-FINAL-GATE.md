# NEX M01 · Final reference-lab gate

**Status:** `M01_REFERENCE_LAB_COMPLETE / OWNER_APPROVED_BUDGET / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-15 · **Base:** `900d2b2d031a87048702625a1e98bc50905bc663`
**Parent:** #6 · **Sub-issues:** #21 S01, #22 S02, #23 S03, #24 S04, #25 S05, #26 S06, #27 S07.

## O que foi concluído

| Sub-issue | Entrega | Evidência |
|---|---|---|
| #21 S01 | Cenas, câmera, seeds, materiais/luzes, imagens de aceitação 1920×1080 | `golden-matrix.v1.json` / `GOLDEN-MATRIX.md`; `LICENSE-AUDIT.md` |
| #22 S02 | FramePulse sintético integrado | PR #95 / checkpoint S02 |
| #23 S03 | Golden matrix 18 capturas, A/A byte-idêntico, A/B + 6 regiões | `golden-matrix.v1.json` / `GOLDEN-MATRIX.md` |
| #24 S04 | Stress ARPG e matriz física RTX 5050 | PR #107 / #110 / #112 |
| #25 S05 | Matriz cinematográfica 15/15 capturas | PR #120 |
| #26 S06 | Radar R&D NEX-RD-01..10 | PR #119 |
| #27 S07 | Baseline, audit pack, budget 1080p aprovado | `final-budget.v1.json` / `FINAL-BUDGET.md`; `manifest.json` |

## S01 · aceitação por cena

| Cena | Seed | Imagem | SHA-256 | Backend |
|---|---:|---|---|---|
| corridor_static | 4101 | `corridor_static_ab-low_1.png` | ver `golden-matrix.v1.json` | Vulkan / Forward+ / RTX 5050 |
| arena_combat | 4102 | `arena_combat_ab-low_1.png` | ver `golden-matrix.v1.json` | Vulkan / Forward+ / RTX 5050 |
| dense_city | 4103 | `dense_city_ab-low_1.png` | ver `golden-matrix.v1.json` | Vulkan / Forward+ / RTX 5050 |

As três cenas têm **0 recursos externos**; a auditoria de licenças está em `LICENSE-AUDIT.md`.

## S03 · golden matrix

- **18 capturas nativas 1920×1080** (3 cenas × 2 presets × 3 repetições).
- **A/A byte-idêntico** em todas as células.
- A/B (ab-low vs ab-high): mean abs **0.4168 / 0.4215 / 0.1785**; pixels alterados **3.367% / 3.354% / 1.276%**; PSNR **38.485 / 36.851 / 40.464 dB**.
- Regiões fixas: full, center_gameplay, top/bottom/left/right bands; o centro de gameplay concentra a maior diferença (corridor **7.845%** de pixels).
- Aprovação visual registrada como `OWNER_APPROVED_ADMIN_SOLO`; não é uma métrica de qualidade artística.

## S07 · orçamento 1080p aprovado

| Cena | GPU p95 | CPU p95 | Pacing p95 | 1% low | Checks |
|---|---:|---:|---:|---:|---|
| corridor_static | 0.139 ms | 0.395 ms | 4.273 ms | 223.26 FPS | PASS |
| arena_combat | 0.151 ms | 0.382 ms | 4.291 ms | 224.27 FPS | PASS |
| dense_city | 0.122 ms | 0.363 ms | 4.255 ms | 223.76 FPS | PASS |

Tetos aprovados: GPU p95 ≤ 1.0 ms; CPU p95 ≤ 2.0 ms; pacing p95 ≤ 16.67 ms (60 FPS); 1% low ≥ 60 FPS; meta experimental 120 FPS: pacing p95 ≤ 8.33 ms e 1% low ≥ 120 FPS. **Decisão do Owner:** `OWNER_APPROVED` em 2026-11-15.

## Recomendações para os próximos módulos

- **M02:** usar as imagens S01 como baseline de câmera e aplicar A/B/A no mesmo viewport/backend; não comparar sessões com pacing diferente.
- **M03:** comparar luzes/sombras/fog contra o preset `ab-low`/`ab-high` do golden matrix, registrando GPU p95 e legibilidade.
- **M04:** o kit procedural está pronto como dados; falta aplicar materiais em cena e medir custo real.
- **M05:** o dataset de FX e o budget planner estão prontos; falta a camada de partículas real.
- **M06:** o atlas atual cobre M09; a próxima medição deve classificar CPU/GPU/VRAM por cena usando este budget como referência.

## Limitações

- Sessão única, uma GPU (RTX 5050) e um driver (NVIDIA 617.14); frame estático.
- O workload é leve (100 meshes) e o pacing é limitado por `max_fps=240`; não é uma promessa de 60/120 FPS em jogo.
- A comparação PNG é sinal de regressão, não qualidade artística.
- A aprovação é `ADMIN_SOLO / NOT_INDEPENDENT`; não há revisor humano independente.
- O M01 conclui o **laboratório de referência**, não a engine inteira nem os módulos M02–M12.

## Fechamento

Com este gate, as issues **#21, #23, #27 e #6** podem ser fechadas como `COMPLETED`; #22/#24/#25/#26 já estavam concluídas. O checkpoint registra `m01FinalReference` e mantém os demais parents no escopo bounded.
