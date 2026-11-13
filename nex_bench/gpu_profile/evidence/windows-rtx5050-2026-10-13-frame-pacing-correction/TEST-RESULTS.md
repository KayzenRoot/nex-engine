# Testes e verificações

## Suítes Python executadas no Windows local

- tests/ci: 97 testes, PASS (inclui cobertura negativa e compatibilidade v1).
- tests/contracts: 12 testes, PASS.
- tests/telemetry: 31 testes, PASS.
- Total: 140 testes, todos aprovados. Saídas integrais em PYTHON-CI.log, CONTRACTS.log e TELEMETRY.log.

A regressão exercita intervalos monotônicos variáveis e hitch simulado; confirma que o 1% low deriva da série monotônica, separado do delta VSync-limited; rejeita zero, timestamp ausente e rollback; falha fechada sem low/COMPLETE quando o clock está inválido; e cobre cancelamento sem exportação parcial como COMPLETE. Os 12 perfis v1 mantidos no bundle anterior continuam validados pelo teste de compatibilidade.

## Smoke nativo

Godot oficial 4.7.2 Windows, execução local via Start-NEX.ps1 -SmokeOnly, exit code 0. O log contém PASS para diagnóstico F9, navegação da câmera, observação de frames, variação/hitch monotônico, zero/rollback como UNAVAILABLE, cancelamento, heatmap, visual truth e importação headless. O smoke terminou em NEX_NATIVE_STARTUP_VALIDATED.

## Integridade local

- Todos os seis JSON v2 foram revalidados individualmente: PASS.
- 12 capturas brutas anteriores: Git blobs iguais ao pai 89913fe950cd1dee4c53be62fb94ce54d747937f; nenhum arquivo antigo foi editado ou removido.
- git diff --check: exit 0.
- Verificações de provedor do GitHub para o novo HEAD só serão reportadas após o push e sua conclusão.