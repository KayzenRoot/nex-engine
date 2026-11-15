# NEX-M02-FINAL-REFERENCE-WO-001 | Fechamento do renderer de referência M02

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0013` / `NEX-D-023`; instrução do Owner de 2026-11-15 para finalizar os módulos base após o M01.
**Base:** `main` `fa1adae7ab67e38c2556d126627006c338e2e8f4`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (capturas e medições nativas M02).
**Lock:** `.engineering/context-locks/NEX-M02-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M02 como renderer de referência: câmera S01 com aspect ratios/3D↔tela, sightline S02 com reveal renderizado, DepthWeave S03 com overlay alpha, TemporalGuard S04 com TAA nativo off/on e compositor customizado NO_GO, RenderPassport S05 com passport runtime/perfis, S06 R&D e S07 QA/gate; fechar #28–#34 e #7 após integração protegida.

## Escopo

- Flags aditivas no harness `preset_ab.gd`: sightline, depth overlay, TAA e profiles.
- `nex_bench/scenes/m02_camera/camera_math.gd` e `nex_bench/scenes/m02_temporal/analyze_taa.gd`.
- `nex_modules/render3d/profiles/runtime_probe.gd`.
- Evidence bundles `windows-rtx5050-2026-11-15-m02-camera-aspects`, `...-sightline`, `...-sightline-perf`, `...-depth`, `...-depth-perf`, `...-temporal-taa`, `...-profiles`, `...-profiles-perf`.
- `docs/benchmarks/m02/tools/build_m02_runtime.py`, `runtime.v1.json`, `RUNTIME.md`, `M02-FINAL-GATE.md`.
- QA ledger S01–S05, README, REGRESSION-REPORT, QUALITY-LEDGER.
- `tests/ci/test_m02_final.py`, ajustes no QA ledger/enforcement.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de issues.

## Fora de escopo

- Renderer/runtime de M03–M12, shader/compositor customizado, GI, sombras/VFX reais.
- Jogo, gameplay, rede, cena de produção, asset de terceiros.
- Claims generalizados de FPS/qualidade, cross-device ou input-to-photon.
- M12/marca.

## DoD

- S01: round-trip < 0.01 m, fast follow < 250 px, 4 aspect ratios.
- S02: reveal 0→1 nas 3 cenas, A/B visual e GPU delta documentado.
- S03: overlay alpha com 0 z-fight/alpha/overlay e GPU delta documentado.
- S04: TAA off/on capturado; compositor customizado NO_GO; performance INCONCLUSIVE.
- S05: passport RUNTIME_PROBED; quality/balanced/performance aplicados e medidos.
- QA ledger S01–S05 com evidência; builder `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issues #28–#34 e #7 fechadas com comentário de evidência.

## STOP

- Base/HEAD divergente, captura não determinística, validação canônica falhando, perfil sem reversibilidade, check vermelho ou claim generalizado → parar e registrar.
