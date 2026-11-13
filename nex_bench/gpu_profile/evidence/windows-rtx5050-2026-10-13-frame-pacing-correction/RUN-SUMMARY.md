# Resultado das medições reais

**Código medido:** commit 179ede475fa8ef13bbaaeb9af3e37caf373e0d51 (tree 2079128d9df5400a03cda4043e55ff8a5c36cacf). **PR:** #107. **Base:** main 226b015ed34d8e4452819da45f92d8936796b3b0.

Godot 4.7.2 GUI executou seis capturas seriais completas, três em cada um dos dois workloads afetados pela correção. Cada perfil foi revalidado pelo validador Python do repositório: schema v2, COMPLETE, FRAME_PACING_INTERVAL_MS MEASURED, zero amostras inválidas, origem no commit medido e status PASS.

| Cenário | Run ID | Segundos observados | Intervalos monotônicos válidos | Valores distintos | 1% low v2 (FPS) |
|---|---|---:|---:|---:|---:|
| Density Ladder, 200 geometry | 1791883867-295809379 | 30.007211 | 2250 | 581 | 66.866880 |
| Density Ladder, 200 geometry | 1791883979-407576457 | 30.006411 | 2250 | 668 | 71.246914 |
| Density Ladder, 200 geometry | 1791884017-445689369 | 30.006254 | 2249 | 678 | 68.236907 |
| Density Ladder, 25 combined | 1791884095-523815570 | 30.006566 | 2250 | 592 | 68.335438 |
| Density Ladder, 25 combined | 1791884133-561569147 | 30.008495 | 2250 | 482 | 68.928521 |
| Density Ladder, 25 combined | 1791884170-598874419 | 30.004080 | 2250 | 489 | 69.359002 |

A fórmula v2 calcula 1000 dividido pela média aritmética dos intervalos positivos mais lentos, usando ceil(1% de n), na série FRAME_PACING_INTERVAL_MS. A série MAIN_LOOP_INTERVAL_MS baseada em delta permanece apenas como diagnóstico e a métrica derivada dela é identificada como DELTA_DERIVED_VSYNC_LIMITED.

As seis execuções ocorreram com VSync=1 e max_fps=0. Os resultados são apresentados por cenário, sem usá-los como comparação de desempenho entre workloads. Interrupções abaixo de 12 FPS por 5 s não ocorreram.

A API monotônica mede o intervalo entre callbacks ativos de _process. Ela não mede apresentação efetiva, latência input-to-photon nem pacing físico do display. Médias e 1% low aqui são evidência da série de callbacks e têm esse limite explícito.

As 12 capturas brutas v1 já existentes foram verificadas contra o pai 89913fe950cd1dee4c53be62fb94ce54d747937f: todos os Git blobs permaneceram idênticos. Seus SHA-256 constam em PRESERVED-12-CAPTURES-SHA256.txt.