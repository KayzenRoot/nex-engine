# Evidence Bundle · NEX-M02-S03-WO-001 (DepthWeave prototype)

**Status:** `PROTOTYPE_EVIDENCE / NO_RENDERING / NO_SHADER_CHANGE / NO_2.5D / NO_PERFORMANCE_CLAIM`
**Issue:** #30 · **Base:** `7a9d33f4aab4062b14380828bdcd00035ebaa92a` · **Code SHA:** `68378db625386f3dffc961ed55881c1ddcf5ed12`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/render3d/depth_composition/`: projeto Godot autocontido com `depth_composition_solver.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, `M08-COMPOSITION-CONTRACT-DRAFT.md` e log headless.
- `tests/ci/test_depth_composition.py`: 8 testes estruturais (arquivos, projeto, API/chaves do plano, passes/histerese, ausência de atalho de rendering, marcador/evidência, limites/draft, ausência de claim fabricado).

## Verificação executada

Comando (Godot oficial 4.7.2, binário `ab1824f8…`):

```powershell
& "<pinned Godot>" --headless --path nex_modules/render3d/depth_composition `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M02_S03_SMOKE_PASS: 37 checks`** (exit 0), log em `nex_modules/render3d/depth_composition/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 37 checks:
- configuração/câmera/registro inválidos (projeção, epsilon/histerese, limite, direção degenerada, duplicata, raio negativo, kind inválido, max primitives);
- opaco/decal front-to-back, alfa back-to-front, overlays por último, desempate por id;
- Z-fighting detectado e resolução determinística/repetível;
- histerese: inversão pequena estabilizada, inversão grande muda a ordem;
- câmera lenta estável e passo rápido com flip de ordem;
- alfa à frente de crítico sinalizado; alfa atrás não;
- overlay que bloqueia gameplay sinalizado; overlay seguro não;
- projeção ortográfica registrada e ordenação consistente;
- limpeza, limites documentados no plano e serialização da câmera.

## O que não foi feito / não é alegado

- **Sem rendering/screenshots/visual human gate**: bordas, aliasing, transparência real e passagens estreitas são `INCONCLUSIVE_NOT_RUN`.
- Primitivas são esferas mock com profundidade no eixo de visão; bounds reais por pixel exigem WO de integração de cena.
- `alpha_over_critical` é conservador (profundidade, não cobertura de pixel); é aviso, não prova.
- Ortográfica e perspectiva compartilham a ordenação neste protótipo.
- Sem shader/material/M04/2.5D/engine/CI; sem FPS/VRAM/frame-time.
- O draft M08 é `DRAFT_NOT_PROMOTED`; não admite M08.

## Rollback

Remover `nex_modules/render3d/depth_composition/**`, `tests/ci/test_depth_composition.py`, este bundle e o delta. Nenhum arquivo de M01, câmera S01, Sightline S02, contratos, CI ou checkpoint é alterado.

## Próximos passos

- M02-S04 (TemporalGuard) pode consumir o plano/histerese como mock.
- Integração real de cenas/depth buffer e o gate visual exigem WO própria.
- Qualquer medição visual/frame-time deve usar o baseline M01 e o mesmo hardware/procedimento.
