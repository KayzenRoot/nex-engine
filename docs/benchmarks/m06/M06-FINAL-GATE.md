# NEX M06 · Final performance gate

**Status:** `M06_PERFORMANCE_REFERENCE_COMPLETE / OWNER_AUTHORIZED / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-16 · **Base:** `c763319d04d0bf353c15db8378872bdf8fab1734`
**Parent:** #11 · **Sub-issues:** #59 S01, #60 S02, #61 S03, #62 S04, #63 S05, #64 S06, #65 S07, #66 S08, #67 S09, #68 S10.

## O que foi concluído

| Sub-issue | Entrega | Evidência |
|---|---|---|
| #59 Bottleneck Atlas | 33 runs classificados em GPU/pacing | `m06-runtime.v1.json` S01 |
| #60 BatchWeave | MultiMesh e grupos espaciais | 9 runs; draw calls 385→223 no corredor |
| #61 LOD Governor | High vs governor com histerese | 6 runs; GPU -8.17%/-7.10%/-1.00% |
| #62 Occlusion Mapper | Frustum/AABB ON/OFF | 6 runs; NO_GO para mapper customizado |
| #63 StreamGuard | Async loader + cache + falha | 17 checks; 14.0–21.0 ms |
| #64 FramePacer | Política de render scale | 3 runs; GPU -15.41%/-28.23% |
| #65 Performance R&D | Matriz GO/NO_GO | `m06-runtime.v1.json` S07 |
| #66 Performance QA | 33 runs, 27 imagens, 3 smokes | `m06-runtime.v1.json` S08 |
| #67 VRAM Sentinel | Monitor + histerese + carga de texturas | 9 checks; +198.9 MB |
| #68 FillRate X-Ray | Matriz eventos × resolução | 9 runs; 1440p +135.9% vs 720p |

## Resultado

- **S01:** 33 runs; 22 GPU, 11 pacing; nenhum caso `memory` ou `insufficient_data`.
- **S02:** MultiMesh mantém a imagem visualmente idêntica (0.000% de pixels) e reduz draw calls 385→223; CPU p95 -6.1% no corredor.
- **S03:** LOD Governor reduz GPU p95 8.17%/7.10%/1.00%; custo visual 3.458%/4.314%/0.967%; 1% low do corredor cai 39.39%.
- **S04:** mapper customizado não reduz GPU; arena tem 2.284% de pixels escondidos incorretamente; oclusão real `INCONCLUSIVE_NOT_BAKED`.
- **S05:** StreamGuard 17 checks; três cenas prontas em 14.029/14.031/20.954 ms; uma falha esperada para path ausente.
- **S06:** render scale 0.85/0.70 reduz GPU 15.41%/28.23%; pixels 2.478%/3.748%; política dinâmica não habilitada.
- **S09:** engine video memory 12.605.824 → 211.489.664 bytes ao carregar 22 texturas; estado `OK` com ratio 0.0352.
- **S10:** 1440p +135.9% vs 720p em 1 evento; 100 vs 1 evento em 1080p +11.1%; overdraw é proxy, não contador de fragmentos.
- **Decisões:** Bottleneck Atlas/BatchWeave **GO**; LOD/StreamGuard/FramePacer/VRAM/FillRate `GO_WITH_LIMITATIONS`; Occlusion Mapper customizado **NO_GO**.

## Limitações

- Sessão única, RTX 5050, driver NVIDIA 617.14; 1920×1080 salvo indicação.
- LOD Governor é experimento bounded, não o LOD automático do Godot nem um engine de produção.
- Oclusão real exige occluders baked e não foi exercitada.
- Sem render scale dinâmico, shader prewarm, eviction de VRAM, streaming de cena ou prefetch de disco.
- Draw calls são contadores do engine, não prova de pipeline por material.
- Overdraw é proxy determinístico, não fragment counter.
- **Nenhum asset de terceiros. Nenhuma paridade com PoE2 é alegada.**
- Nenhum claim generalizado de FPS/qualidade ou cross-device.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Fechamento

Com este gate, as issues **#59–#68 e #11** podem ser fechadas como `COMPLETED` após o merge protegido e os checks pós-merge. O próximo módulo base é **M07** (render2d/canvas), que deve consumir as medições e os limites M06; M08–M12 continuam bounded.
