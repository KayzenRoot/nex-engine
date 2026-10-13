# NEX Engine S04 | Evidências físicas R9 — pacote parcial

**Status: `BLOCKED` — interrupção após resultado físico inválido. Este pacote não qualifica a aceitação R9.**

## Identidade e ambiente

- Repositório/PR/branch: `KayzenRoot/nex-engine`, PR #107, `feat/nex-m01-s04-gpu-profile-delta-001`.
- SHA do código medido: `d59c94da13839ba1c6c2e894d4d1147ff3fddc78`; base protegida `main`: `226b015ed34d8e4452819da45f92d8936796b3b0`.
- Sistema: Windows 11 Pro, build 26300. Godot oficial: `4.7.2.stable.official.ed1daf0bf`; executável SHA-256 `ab1824f85bfd8e0e4128182c000c4003a3e042245b2967848d089b2a04b22424`.
- GPU: NVIDIA GeForce RTX 5050; driver 617.14. Renderer observado no F9: `forward_plus` / Vulkan; viewport `1280×720`; VSync 1; limite máximo 0. A memória do `nvidia-smi` é do dispositivo/WDDM e não é atribuída ao processo.
- F9 antes da sessão (cena Corridor): 75 FPS observados, 49 draw calls, 631 objetos 3D e 87,5 MiB de alocação do renderer. A própria interface identifica FPS como não benchmark e a alocação como distinta de VRAM total.
- `Start-NEX.ps1` iniciou a GUI com exit 0 e registrou `NEX_NATIVE_IMPORT_SMOKE_PASS`; Godot PID 5964 fechou ao terminar. Snapshot após fechamento: RTX 5050, 617.14, 1%, 39 °C, 1.152 MiB totais reportados por WDDM.
- Os mutexes `Local\NEX_M01_S04_GPU_PROFILE_WRITER` e `Local\NEX_M01_S04_GPU_PROFILE_RTX5050` foram adquiridos exclusivamente e depois verificados livres. O fechamento do processo de lease precisou de recuperação porque o transporte exec fechou stdin; isso está documentado em `EXCLUSIVE-LEASE-CLOSEOUT.txt`. Nenhuma outra sessão Godot ou agente concorrente foi observada.

## Capturas físicas

Cada tentativa positiva pediu 2 s de aquecimento e 30 s de observação, foi executada em série, no mesmo processo, e teve seu JSON bruto validado pelo validador v2 via stdin em bytes originais. `PASS` do validador no run inválido significa que o estado `INVALID` foi corretamente classificado; não significa captura física aprovada.

| # | ID | Carga | Estado | Observação | Samples pacing válidas/inválidas | GPU/CPU | 1% low FPS* |
|---:|---|---|---|---:|---:|---|---:|
| 1 | `1791932529-210208543` | 25 / geometry | `COMPLETE` / `requested_observation_window_elapsed` | 30.008s | 2250/0 | MEASURED/MEASURED | 59.07 |
| 2 | `1791932692-373124913` | 25 / geometry | `COMPLETE` / `requested_observation_window_elapsed` | 30.006s | 2250/0 | MEASURED/MEASURED | 59.23 |
| 3 | `1791932752-433667500` | 25 / geometry | `COMPLETE` / `requested_observation_window_elapsed` | 30.007s | 2250/0 | MEASURED/MEASURED | 58.19 |
| 4 | `1791932802-483419600` | 100 / geometry | `COMPLETE` / `requested_observation_window_elapsed` | 30.007s | 2250/0 | MEASURED/MEASURED | 69.13 |
| 5 | `1791932845-526668766` | 100 / geometry | `COMPLETE` / `requested_observation_window_elapsed` | 30.007s | 2250/0 | MEASURED/MEASURED | 64.31 |
| 6 | `1791932894-574871020` | 100 / geometry | `COMPLETE` / `requested_observation_window_elapsed` | 30.007s | 2250/0 | MEASURED/MEASURED | 60.38 |
| 7 | `1791932946-627102729` | 200 / geometry | `COMPLETE` / `requested_observation_window_elapsed` | 30.007s | 2250/0 | MEASURED/MEASURED | 57.51 |
| 8 | `1791933058-739560811` | 200 / geometry | `COMPLETE` / `requested_observation_window_elapsed` | 30.006s | 2250/0 | MEASURED/MEASURED | 62.56 |
| 9 | `1791933080-760888025` | 200 / geometry | `INVALID` / `invalid_monotonic_tick` | 0.000s | 0/1 | UNAVAILABLE/UNAVAILABLE | — |

*1% low vem da série monotônica de callbacks `_process`; não é tempo de apresentação do monitor nem input-to-photon. Não há alegação de ganho de desempenho.*

### Parada e critérios ainda não executados

A tentativa 9, run `1791933080-760888025`, terminou imediatamente como `INVALID / invalid_monotonic_tick`. A série `FRAME_PACING_INTERVAL_MS` declarou `UNAVAILABLE / invalid_monotonic_tick_sequence`, 0 amostras válidas e 1 inválida; GPU/CPU ficaram indisponíveis e a observação foi 0 s. O validator v2 retornou exit 0 / `PASS` para a classificação inválida. A tela F12 mostra `GPU profile INVALID`. A causa subjacente do tick inválido não foi determinada; não houve retry nem alteração do código.

- 25 geometry: 3/3 `COMPLETE`; 100 geometry: 3/3 `COMPLETE`; 200 geometry: 2/3 `COMPLETE` e 1/3 `INVALID` (conta 2/3 aprovadas).
- 25 combined: 0/3; não executado. Terceira repetição de 200 geometry: não executada após o inválido.
- Negativo real de redimensionamento da janela durante F11: não executado. Rejeição imediata Combined 50: não executada.

## Verificações locais

- `Start-NEX.ps1` nativo: exit 0; smoke markers registrados no log Godot, inclusive import, GPU profile e visual heatmap.
- Validador GPU Profile v2: os oito relatórios `COMPLETE` passaram; o nono relatório inválido passou apenas na validação estrutural/classificação `INVALID`.
- `tests/contracts`: 12/12 PASS; `tests/telemetry`: 31/31 PASS.
- `tests/ci`: 106 testes, 100 passaram e 6 falharam na asserção SHA-256 das seis capturas v2 da pasta `frame-pacing-correction`. Diagnóstico: Git global `core.autocrlf=true` converteu LF→CRLF somente nos bytes do novo checkout Windows; os 18 blobs de `HEAD` e os 18 arquivos do worktree original preservam exatamente os hashes esperados. Evidência completa: `HISTORICAL-PRESERVATION-CHECK.txt`. Nenhum arquivo histórico foi regravado.
- Checks GitHub do novo HEAD: aguardando após publicação deste pacote. Os 13/13 checks do HEAD anterior não substituem a validação do novo HEAD.

## Integridade e escopo

- O worktree original permaneceu em `39e53fb4e34a536fa9b163c4373abd2c2cb88960`, com os mesmos arquivos históricos/capturas não rastreados; não houve reset, stash, clean, checkout forçado nem alteração nesse worktree.
- O worktree isolado iniciou limpo e detached em `d59c94da13839ba1c6c2e894d4d1147ff3fddc78`; mudanças criadas para este pacote ficam apenas em `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-10-13-r9-qualification/`. O SHA do commit que contém este relatório é disponibilizado pelo HEAD final da PR.
- Nenhum código, validador, configuração global, `main`, checkpoint ou histórico de aceitação foi alterado. Sem merge.

## Resultado

`BLOCKED` — resultado inválido no frame pacing; matriz positiva incompleta, negativos reais ausentes e suíte CI local com divergência de bytes por `core.autocrlf`. A sessão física encerrou, a GUI fechou e ambos os mutexes foram liberados/verificados livres. Este bundle contém apenas os dados autênticos coletados e não declara `READY_FOR_EXACT_HEAD_REVIEW`.
