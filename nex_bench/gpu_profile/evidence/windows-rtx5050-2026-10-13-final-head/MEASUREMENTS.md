# Medições locais do GPU Profiler — HEAD 3892fbe

12 execuções capturadas com Godot 4.7.2 e RTX 5050. Cada perfil é de uma sessão sequencial e independente, com 2 s de aquecimento descartado e pelo menos 30 s observados. Todos os 12 arquivos passaram pelo validador local; os valores da tabela vieram dos JSONs brutos.

| Carga | Efeito | Run ID | Segundos | GPU p95 (ms) | CPU p95 (ms) | 1% low (FPS) | Amostras GPU |
|---:|---|---|---:|---:|---:|---:|---:|
| 25 | geometry | 1791861284-94123612 | 30.013 | 0.122 | 0.292 | 75.000 | 2251 |
| 25 | geometry | 1791861329-139216409 | 30.013 | 0.122 | 0.278 | 75.002 | 2251 |
| 25 | geometry | 1791861370-179258950 | 30.013 | 0.122 | 0.297 | 75.000 | 2251 |
| 100 | geometry | 1791861416-225833049 | 30.013 | 0.195 | 0.297 | 75.002 | 2251 |
| 100 | geometry | 1791861457-266323495 | 30.013 | 0.195 | 0.286 | 75.000 | 2251 |
| 100 | geometry | 1791861498-308227035 | 30.013 | 0.195 | 0.293 | 75.002 | 2251 |
| 200 | geometry | 1791861543-352488133 | 30.013 | 0.296 | 0.301 | 75.000 | 2251 |
| 200 | geometry | 1791861586-395620628 | 30.013 | 0.296 | 0.319 | 75.002 | 2251 |
| 200 | geometry | 1791861628-438132686 | 30.013 | 0.296 | 0.312 | 75.002 | 2251 |
| 25 | combined | 1791861677-486406171 | 30.013 | 0.213 | 0.353 | 75.002 | 2251 |
| 25 | combined | 1791861719-528357532 | 30.013 | 0.213 | 0.345 | 75.002 | 2251 |
| 25 | combined | 1791861761-570303070 | 30.013 | 0.213 | 0.344 | 75.002 | 2251 |

## Interpretação

- A tabela registra medições do RenderingServer por viewport e de CPU/render; o tempo de render por viewport não é input-to-photon.
- A configuração do perfil era max_fps=0 e vsync_mode=1. A UI observou aproximadamente 72–75 FPS nas execuções (um limite compatível com VSync); esses valores não são resultado de benchmark de capacidade.
- A memória do renderer reportada na UI foi 88,1 MiB; isso não é VRAM total. O snapshot nvidia-smi é device-wide sob WDDM e não atribui memória/uso ao processo Godot.
- O painel F9 salvo mostra, naquele instante, RTX 5050, Forward+/Vulkan, Windows, 75 FPS observados (não benchmark), CPU de processo 15,73 ms/frame (não GPU time), 32 draw calls, 794 objetos 3D e 88,1 MiB de alocação do renderer.
