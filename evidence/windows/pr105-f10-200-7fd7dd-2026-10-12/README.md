# Evidência F10 — 200 entidades no HEAD corrigido

## Resultado

**PASS — captura F10 real no Windows com RTX 5050, no código fonte exato `7fd7ddbac890261a8c22cd10f72431bc5add5ca3`.** A cena F4 registrou 200 proxies em modo `geometry`. O JSON bruto foi copiado byte a byte do arquivo recém-criado; o original continua no diretório local do Godot. O validador oficial leu esse arquivo original pelo stdin e retornou `status=PASS`, exit code `0`.

Foram coletados 601 intervalos em 8.013133 segundos. Os percentis recalculados foram p50/p95/p99 = 13.333 ms; média observada de 75.001875 FPS. O F9 identificou `NVIDIA GeForce RTX 5050`, `forward_plus / Vulkan`, Windows, driver NVIDIA 617.14. O viewport era 1280x720, VSync mode 1 e max FPS configurado em 0. A tela F4/F9 registra renderer, backend e a carga de 200 proxies.

Os intervalos são deltas do loop principal. A cadência observada de aproximadamente 75 FPS coincide com VSync e **não é frametime da GPU, memória total de VRAM ou FPS máximo sem limite**. A memória mostrada pelo F9 é alocação do renderer e não representa VRAM total.

## Proveniência

- PR: `#105`, branch `feat/nex-m01-windows-one-click-launcher`.
- Base `main`: `a71df4c141ac52cc59778dc0f08831458d62ef33`.
- Código testado: `7fd7ddbac890261a8c22cd10f72431bc5add5ca3`.
- Árvore do código testado: `c3c98f16f62fe1bbeecd4b91bf5860cbb767cae6`.
- Godot: `4.7.2-stable`, commit oficial `ed1daf0bf001b61586d9930840f2f1394092c079`.
- SHA-256 do executável Godot, hardware e driver: `GPU-SNAPSHOT.txt`.
- `Start-NEX.log` registra a validação local e a abertura da GUI. `Godot-GUI.log` registra Vulkan 1.4.351 / Forward+ / NVIDIA RTX 5050.

## Conteúdo

- `F10-200-geometry.json`: novo JSON bruto da única captura feita para este delta.
- `F10-validator-output.txt`: saída integral do validador oficial; `PASS`.
- `F10-pre-run-inventory.txt`: hashes das cinco capturas existentes antes do replay.
- `F10-source-inventory.txt`: nome, tamanho, horário UTC e hash do arquivo original recém-gerado.
- `F4-200-geometry-F9-before-capture.jpg`: tela real da GUI com F4/200 geometry e painel F9.
- `F9-RTX5050-200-7fd7dd.jpg`: tela real do painel F9 após iniciar o projeto nesta revisão.
- `Start-NEX.log` e `Godot-GUI.log`: logs reais da execução local.
- `GPU-SNAPSHOT.txt`: ambiente e configuração capturados.
- `SHA256SUMS.txt`: SHA-256 dos arquivos deste pacote, exceto o próprio manifesto.

As cinco capturas de cenários anteriores foram apenas inventariadas antes e depois; todas mantiveram seus hashes e nenhuma foi repetida ou incluída novamente.