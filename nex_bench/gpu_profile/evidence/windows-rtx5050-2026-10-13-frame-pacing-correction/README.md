# Correction Delta de frame pacing — evidências

Este pacote acompanha a correção da PR #107. O código medido está no commit 179ede475fa8ef13bbaaeb9af3e37caf373e0d51, árvore 2079128d9df5400a03cda4043e55ff8a5c36cacf, base main 226b015ed34d8e4452819da45f92d8936796b3b0.

- RUN-SUMMARY.md: seis execuções reais, três por cenário afetado, com contagens e resultados.
- PROVENANCE.md: sistema, Godot oficial, GPU, driver, configuração e limites de interpretação.
- TEST-RESULTS.md: suítes automatizadas, smoke nativo e regressões negativas.
- gpu_profile_*.json: seis perfis brutos v2, coletados no Godot GUI; cada um acompanhado de .validation.json.
- GUI-STATE-MAXIMIZED.png e GUI-STATE-COMBINED-25.png: confirmação visual dos dois cenários.
- RTX5050-*-REPEATS.log: snapshots da GPU e registro das execuções repetidas.
- PRESERVED-12-CAPTURES-SHA256.txt: SHA-256 e Git blob de cada uma das 12 capturas anteriores, comparados ao pai da correção.
- SHA256SUMS.txt: hashes deste Evidence Bundle (exceto o próprio arquivo).

Os valores de pacing são intervalos monotônicos observados por callback em _process e não tempo de apresentação no monitor. A 1% low v2 usa somente esses intervalos. Os resultados não afirmam latência input-to-photon nem tempo de frame apresentado.