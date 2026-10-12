# NEX Engine PR #105 — Evidence Bundle de validação Windows/F10

**Data:** 2026-10-12
**PR:** https://github.com/KayzenRoot/nex-engine/pull/105
**Branch:** `feat/nex-m01-windows-one-click-launcher`
**Review técnico executado:** https://github.com/KayzenRoot/nex-engine/pull/105#pullrequestreview-5496655093
**Base confirmada:** `a71df4c141ac52cc59778dc0f08831458d62ef33` (`main`)
**HEAD inicial pedido e usado para executar o laboratório:** `ea94eb98666966ce8c376df436dbfdd33c6da06f`
**Tree do runtime testado:** `e0d57025928479468f52184128b73c812b950fea`
**Correção do teste Windows commitada:** `9c17fc5b763619ef230f8f89a6bfb6b66a3b4518` (tree `6aeea09aba8069ea8c09b183ce8c0cf0a294f2ef`). O conteúdo runtime da Godot não mudou entre `ea94...` e a correção.

## Test Matrix e resultado por critério

A matriz linha a linha está em `TEST-MATRIX.md`. O `CHECKPOINT-DELTA-PROPOSED.md` é apenas sugestão anexada; checkpoint canônico não foi modificado.

| Critério | Resultado e evidência |
|---|---|
| Branch, base e HEAD | PASS. O HEAD inicial remoto era `ea94eb98666966ce8c376df436dbfdd33c6da06f`, e a base era `a71df4c141ac52cc59778dc0f08831458d62ef33`. A correção ficou na branch da mesma PR. |
| Godot 4.7.2 oficial e integridade | PASS. Godot reportou `4.7.2.stable.official.ed1daf0bf`; commit oficial pinado `ed1daf0bf001b61586d9930840f2f1394092c079`. SHA-256 do executável usado: `ab1824f85bfd8e0e4128182c000c4003a3e042245b2967848d089b2a04b22424`. O lock registra o SHA-256 esperado do ZIP Windows `731980f9608d61333e5baf54a2ef17210acc7a538446c0cb9969f002aca1e953`. |
| Janela e backend | PASS. Janela GUI permaneceu aberta e responsiva. F9 identificou NVIDIA GeForce RTX 5050, `forward_plus / vulkan`, display Windows e viewport 1280×720. Log: `Godot-GUI.log`; inicialização: `Start-NEX.log`. |
| Cenas F1–F4 | PASS. Corridor, Arena, Dense City e Density Ladder renderizados. Capturas limpas F1, F2, F3 e F4/25 estão incluídas. |
| Câmera | PASS. Órbita com Right mudou o enquadramento; Home restaurou o enquadramento inicial. Capturas `F1-Camera-Orbit.jpg` e `F1-Home-Reset-Heatmap.jpg`. |
| B/N/D e heatmap | PASS. Baseline B e candidato N são PNGs de 1280×720 com hashes distintos; D encontrou 16,944% de pixels alterados (>2/255), MAE 0,012014 e 156154 pixels alterados; o preview/vermelho foi exibido e PNG do heatmap preservado. `F1-BND-Changed-Heatmap.jpg` mostra o preview. |
| Density Ladder F10 | PASS. 25, 50, 100 e 200 proxies em `geometry`; mais 25 proxies em `combined`. Os cinco JSONs originais e as cinco saídas do validador stdin estão incluídos. Cada validação retornou `status=PASS`. Nenhum fallback de segurança foi acionado. |
| Medições F10 | PASS como observação limitada. 25/50/100 geometry: 601 amostras, média/p50/p95/p99 13,333 ms, cerca de 75,002 FPS observados; 200 geometry: 599 amostras, média 13,369 ms, p50/p95 13,333 ms, p99 13,889 ms, cerca de 74,799 FPS; 25 combined: 601 amostras, 13,333 ms e 75 FPS observados. Todos os JSONs declaram `OBSERVED_MAIN_LOOP_DELTA_NOT_GPU_TIME`, viewport 1280×720, VSync `1` e FPS máximo `0`; como VSync limitou a amostragem a ~75 FPS, os valores não demonstram máximo de desempenho nem tempo de GPU. |
| F9/diagnóstico visual | PASS. Screenshot registra 75 FPS observados, 16,94 ms CPU process/frame, 45 draw calls, 521 objetos 3D e 89,5 MiB de alocação do renderer. Os 89,5 MiB não representam VRAM total; 16,94 ms não é GPU time. |
| Testes locais após correção | PASS. Python `Python 3.13.15`: CI 72/72, contratos 12/12, telemetria 31/31; total 115/115. Logs de rerun incluídos. A falha inicial exclusiva de line endings está explicada em `INITIAL-WINDOWS-CRLF-FAILURE.md`. |
| Escopo e governança | PASS. Alterados somente o verificador e seu teste de regressão dentro desta PR; não houve alteração no core, `main`, checkpoint, ruleset, workflows ou permissões. Nenhuma nova issue/PR foi criada e não houve merge. |
| Checks GitHub | 13/13 check-runs passaram no commit do bundle `016a620...`; CodeRabbit indicou review skipped. A matriz e o delta proposto são uma alteração documental posterior; os checks do novo HEAD precisam ser confirmados e constam no comentário de fechamento da PR. |

## Suítes locais após a correção

Executadas em Python 3.13.15, no Windows local:

```powershell
python -m unittest discover -s tests/ci -p 'test_*.py' -v
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
python -m unittest discover -s tests/telemetry -p 'test_*.py' -v
```

Resultados anexos: `Tests-ci-rerun.log` (72/72), `Tests-contracts-rerun.log` (12/12), `Tests-telemetry-rerun.log` (31/31). O conjunto CI também inclui o teste de regressão de normalização CRLF→LF.
## Validação F10

Cada captura F10 foi validada individualmente por stdin, sem editar o JSON:

```powershell
Get-Content -LiteralPath '<arquivo F10 JSON>' -Raw -Encoding UTF8 | python .\nex_bench\validate_frame_observation.py
```

Arquivos: `F10-25-geometry.json`, `F10-50-geometry.json`, `F10-100-geometry.json`, `F10-200-geometry.json`, `F10-25-combined.json`. As saídas estão nos arquivos `*-validation.txt` correspondentes.

## Correção local encontrada durante a execução

O primeiro CI local teve 4 falhas: hashes de cenas calculados em bytes CRLF no Windows eram comparados a hashes canônicos LF. A correção normaliza CRLF→LF no verificador e no teste. O motivo, hashes exemplares e resultado posterior estão em `INITIAL-WINDOWS-CRLF-FAILURE.md`. Não alterei configuração Git para contornar o problema.

## Limites e proveniência

- Windows 11 Pro, build 26300, 64-bit; display primário 2560×1080.
- RTX 5050, driver NVIDIA 617.14. A captura F9 foi feita durante a sessão gráfica. `GPU-SNAPSHOT.txt` registra uma leitura `nvidia-smi` posterior à execução, portanto é somente instantânea.
- A janela F9 mostrou renderer allocation, não VRAM total. F10 coleta deltas do main loop; não mede GPU frametime, input-to-photon ou desempenho máximo.
- Capturas de UI que exibiam caminho absoluto local foram preservadas localmente e excluídas do bundle publicado. Os JSONs F10, imagens de cena limpas, PNGs B/N/heatmap e logs sanitizados/sem caminho pessoal estão incluídos.
- Não houve recompilação da Godot; a versão pinada foi verificada e usada para smoke, GUI e captura F10.
- `SHA256SUMS.txt` contém SHA-256 dos 31 blobs publicados, no conteúdo canônico do Git; o próprio manifesto fica fora da lista.`n- Não há promoção de checkpoint nem admissão de outro módulo nesta entrega.

## Fechamento

**STOP CONDITION:** `PR105_LOCAL_GUI_F10_VALIDATED_AWAIT_EXACT_HEAD_REVIEW_AND_OWNER_SQUASH_AUTHORIZATION`.

A validação local está pronta para auditoria do HEAD exato. Aprovação/merge continuam fora deste fechamento; aguarda-se a auditoria final do candidato e a autorização de squash do owner.
