# Proveniência e ambiente

- Sistema: Microsoft Windows 11 Pro x64, build 26300.
- Godot GUI: 4.7.2-stable (official), commit upstream ed1daf0bf001b61586d9930840f2f1394092c079.
- SHA-256 do executável GUI: ab1824f85bfd8e0e4128182c000c4003a3e042245b2967848d089b2a04b22424.
- SHA-256 do executável console: c8f0a6bc45a19b33541501e57f6f7cd972ab18453743266339d495cbbe846643.
- GPU observada: NVIDIA GeForce RTX 5050; driver 617.14; memória total reportada 8151 MiB.
- API/renderizador: Vulkan / Forward Plus.
- Configuração capturada: VSync mode 1; max_fps 0.
- Perfil de origem: source_sha 179ede475fa8ef13bbaaeb9af3e37caf373e0d51.
- Janela executada: NEX Engine | Unified Visual Lab (DEBUG), processo Godot local.
- Lease exclusivo: mutexes Local\NEX_M01_S04_GPU_PROFILE_WRITER e Local\NEX_M01_S04_GPU_PROFILE_RTX5050 estavam ocupados pelo executor autorizado durante a coleta; aquisição já registrada na Issue #24 no comentário 6142219079.

Os perfis usam nvidia-smi para snapshot de dispositivo. Memória, temperatura e uso são de todo o dispositivo no WDDM e não atribuídos ao processo Godot. Valores reais lidos nos perfis incluíram memória usada de 1300–1400 MiB, utilização observada de 3–7% e temperatura de 41–52 °C. Os logs registram snapshots antes/depois de cada repetição adicional. Esses dados identificam o ambiente e não são métricas de desempenho do processo.

FRAME_PACING_INTERVAL_MS é calculada com Time.get_ticks_usec em cada callback ativo de _process. É pacing de callback da CPU; não representa apresentação do monitor nem input-to-photon. O tempo GPU/CPU por viewport continua sendo uma série separada fornecida pelo RenderingServer. O perfil não foi tratado como medição de latência de display.