# Matriz de testes — PR #105 / validação local Windows

**Ambiente:** Windows 11 Pro build 26300, Godot 4.7.2 official `ed1daf0bf`, NVIDIA GeForce RTX 5050, Vulkan Forward+, viewport 1280×720. Runtime de produto testado no HEAD `ea94eb98666966ce8c376df436dbfdd33c6da06f`; árvore `e0d57025928479468f52184128b73c812b950fea`.

| ID | Teste | Resultado observado | Evidência |
|---|---|---|---|
| M01 | Start-NEX, smoke headless e janela | PASS; código de saída 0; marcadores de diagnóstico, câmera, F10, heatmap e import PASS; processo GUI responsivo | `Start-NEX.log`, `Godot-GUI.log` |
| M02 | F1 Corridor | PASS; cena carregada | `F1-Corridor-GUI.jpg` |
| M03 | F2 Arena | PASS; cena carregada | `F2-Arena-GUI.jpg` |
| M04 | F3 Dense City | PASS; cena carregada | `F3-Dense-City-GUI.jpg` |
| M05 | F4 Density Ladder — 25 geometry | PASS; 601 amostras; média/p50/p95/p99 13,333 ms; 75,002 FPS observados | `F10-25-geometry.json`, validador, `F4-Density-25-GUI.jpg` |
| M06 | F4 Density Ladder — 50 geometry | PASS; 601 amostras; média/p50/p95/p99 13,333 ms; 75,002 FPS observados | `F10-50-geometry.json` e validador |
| M07 | F4 Density Ladder — 100 geometry | PASS; 601 amostras; média/p50/p95/p99 13,333 ms; 75,002 FPS observados | `F10-100-geometry.json` e validador |
| M08 | F4 Density Ladder — 200 geometry | PASS; 599 amostras; média 13,369 ms; p50/p95 13,333 ms; p99 13,889 ms; 74,799 FPS observados | `F10-200-geometry.json` e validador |
| M09 | F4 representative combined — 25 proxies | PASS; 601 amostras; média/p50/p95/p99 13,333 ms; 75 FPS observados | `F10-25-combined.json` e validador |
| M10 | Integridade dos 5 JSON F10 via stdin | PASS em 5/5; cada arquivo teve saída `status=PASS`; os dados brutos não foram regravados | cinco `*-validation.txt`; `SHA256SUMS.txt` |
| M11 | Câmera e visual truth B/N/D | PASS; Right alterou a vista, Home retornou à câmera inicial; B e N são PNG 1280×720 com SHA distintos; D mediu 16,944% alterado, MAE 0,012014, 156154 pixels; heatmap vermelho exportado | `B-Corridor-Original.png`, `N-Corridor-Right-Orbit.png`, `D-Heatmap-Right-Orbit.png`, screenshots F1 |
| M12 | F9 diagnóstico | PASS; RTX 5050 e Vulkan Forward+ reconhecidos; 75 FPS observados, 45 draw calls, 521 objetos e renderer allocation 89,5 MiB | `F1-F9-RTX5050.jpg` |
| M13 | Suíte CI Windows após fix CRLF | PASS 72/72 | `Tests-ci-rerun.log` |
| M14 | Contratos | PASS 12/12 | `Tests-contracts-rerun.log` |
| M15 | Telemetria | PASS 31/31 | `Tests-telemetry-rerun.log` |
| M16 | GitHub checks do commit com correção + bundle (`016a620...`) | PASS 13/13 check-runs; CodeRabbit mostra PASS porém review explicitamente skipped por auto-review desabilitada | comentário final da PR; checks foram reexecutados após a próxima alteração documental |

## Interpretação e limites

Os JSONs mostram `vsync_mode=1`, `max_fps_setting=0` e intervalos de aproximadamente 13,333 ms. Classificação: **CAP_LIMITED por VSync/monitor**; os ~75 FPS não representam máximo de FPS nem GPU frametime. F9 CPU process 16,94 ms/frame não é GPU time. 89,5 MiB é alocação do renderer, não VRAM total. Nenhum safety fallback foi acionado. Não houve alegação de benchmark máximo.

O resultado de M16 se refere ao HEAD `016a620ccbf09293bf0950165f37458e6bf3e9f8`. A adição desta matriz e do delta proposto cria um HEAD documental posterior; os checks desse novo HEAD devem ser conferidos no estado remoto da PR e registrados no comentário de fechamento.
