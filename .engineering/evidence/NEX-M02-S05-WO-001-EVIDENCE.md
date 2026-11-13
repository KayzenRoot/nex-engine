# Evidence Bundle · NEX-M02-S05-WO-001 (RenderPassport prototype)

**Status:** `PROTOTYPE_EVIDENCE / INVENTORY_ONLY / NO_RENDERING / NO_PROJECT_WRITES / NO_REMOTE_HARDWARE`
**Issue:** #32 · **Base:** `d5f01ac910b8531608d1d305a1709e421567e21b` · **Code SHA:** `2613f51d8f3c7befd656a8c87b48ad8b16a46f69`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/render3d/profiles/`: `capability_matrix.v1.json` (9 capacidades, fontes oficiais, estados por renderer), `profiles.v1.json` (quality/balanced/performance, sem "ultra", sem claim de FPS), `render_passport.gd`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_render_profiles.py`: 9 testes estruturais (arquivos/projeto, matriz documentada/fontes, perfis, API/flags, ausência de escrita/network/mapeamento por GPU, marcador/evidência, limites/fallbacks, ausência de claim fabricado).

## Verificação executada

Comando (Godot oficial 4.7.2, binário `ab1824f8…`):

```powershell
& "<pinned Godot>" --headless --path nex_modules/render3d/profiles `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M02_S05_SMOKE_PASS: 87 checks`** (exit 0), log em `nex_modules/render3d/profiles/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 87 checks:
- carregamento/validação de matriz e perfis; 9 capacidades; 3 perfis; default quality;
- inventário válido → passport; probe ausente → `INCONCLUSIVE_NOT_PROBED`; estados documentados unverified;
- probe booleano → `MEASURED_ENABLED`/`MEASURED_DISABLED` + `RUNTIME_PROBED`; mesmo GPU com probes diferentes muda o estado; probe desconhecido ignorado;
- inventários inválidos (renderer/driver desconhecido, Linux, Godot 4.6, VRAM 0, GPU vazia, availability não-bool) → `INCONCLUSIVE`;
- `gl_compatibility` degradado; mesh LOD/visibility/occlusion `UNSUPPORTED`; perfil quality desativa features e lista `degraded_features`;
- fallback Vulkan→D3D12→GL: cadeia e degradação corretas;
- perfis quality/balanced/performance com valores esperados; perfil desconhecido rejeitado;
- troca de perfil com diff e round-trip; reverso; mesmo perfil sem diff; alvo inválido bloqueado;
- matriz/perfis malformados rejeitados sem corromper estado; fontes oficiais presentes; mapa de fallback documentado.

## Flags explícitas

- `project_godot_writes=false` — nenhuma escrita de configuração.
- `personal_hardware_collected=false` — nenhuma coleta remota.
- `gpu_name_implies_capability=false` — capacidade só vem da matriz documentada ou de probe runtime.

## O que não foi feito / não é alegado

- Estados de capacidade são **documentação-derivados e não verificados** sem probe; a matriz não prova suporte no driver real.
- Sem rendering/benchmark/screenshot/GPU/VRAM/frame-time; perfis são configurações, não desempenho medido.
- Tuning de culling/LOD/streaming é M06; GI/sombras M03; PBR M04; VFX M05; 2.5D M08.
- Sem escrita em `project.godot`, CI, engine ou contratos.
- `gl_compatibility` desativa mesh LOD/visibility ranges/occlusion culling nos settings efetivos; re-verificar com probe em WO de integração de cena.

## Rollback

Remover `nex_modules/render3d/profiles/**`, `tests/ci/test_render_profiles.py`, este bundle e o delta. Nenhum arquivo de M01, S01–S04, contratos, CI ou checkpoint é alterado.

## Próximos passos

- M02-S06 (R&D 3D) ou M02-S07 (QA/integração) podem consumir o passport como mock.
- Snapshots S01–S04 podem ser validados contra a matriz em WO futura.
- Qualquer tuning de M06 ou rendering real exige WO própria e medição no baseline M01.
