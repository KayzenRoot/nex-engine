# Evidence Bundle · NEX-M02-S01-WO-001 (isometric camera prototype)

**Status:** `PROTOTYPE_EVIDENCE / NO_ENGINE_INTEGRATION / NO_PERFORMANCE_CLAIM`
**Issue:** #28 · **Base:** `02f94e62eaed0d70642a94a9495dcffad1aba519` · **Code SHA:** `9f8d4ce7b46d6a2ccebdd2b15ce4c0fe3a5412f3`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/render3d/camera/`: projeto Godot autocontido com `camera_rig.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log de evidência.
- `tests/ci/test_isometric_camera.py`: 10 testes estruturais (arquivos, projeto, API, enum sem colisão builtin, labels de contrato, replay serializado, marcador/evidência, README/fallbacks, ausência de claim fabricado).

## Verificação executada

Comando (Godot oficial 4.7.2, binário `ab1824f8…`):

```powershell
& "<pinned Godot>" --headless --path nex_modules/render3d/camera `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M02_S01_SMOKE_PASS: 32 checks`** (exit 0), log em `nex_modules/render3d/camera/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 32 checks:
- configuração válida/inválida (projeção, clips invertidos, zoom, dead zone, bounds);
- estado alinhado ao contrato (`projection`, `position_m`, `target_m`, `view_rotation_degrees`, `viewport`, `stability`, FOV/ortho size);
- distância da câmera e FOV;
- roundtrip mundo↔tela↔mundo;
- aspectos 16:9, 4:3 e 21:9;
- visibilidade de atores (dentro/fora do safe frame);
- limites de zoom (mín/máx);
- zona morta (segura movimento pequeno, move em movimento grande);
- transição rápida sem overshoot e convergência;
- clamp de bounds;
- projeção ortográfica;
- replay determinístico (32 estados idênticos em duas execuções, com zoom inicial serializado).

## O que não foi feito / não é alegado

- **Performance/FPS A/B: `INCONCLUSIVE_NOT_RUN`.** Nenhuma mudança de rendering; nenhuma captura GPU nesta WO. Qualquer número seria fabricado.
- Sem integração em `nex_bench`/engine, sem input mapping, colisão/oclusão, shake ou cinemáticas.
- `pixel_snap` quantiza posição em metros; não é snap subpixel de projeção.
- `visible_margin` é analítico no plano de foco; profundidades diferentes sob perspectiva exigem validação em S02/S03.
- Headless smoke é teste de lógica determinística, não benchmark visual/GPU.

## Rollback

Remover o diretório `nex_modules/render3d/camera/`, o teste `tests/ci/test_isometric_camera.py`, este bundle e o delta proposto. Nenhum arquivo do M01, contrato, CI ou checkpoint é tocado pela implementação.

## Próximos passos

- M02-S02 (Sightline) e S03 (DepthWeave) podem consumir a API/fixação de câmera publicada, com mocks e WOs próprias — não admitidas por este bundle.
- Se a direção for rejeitada, aplicar Fallback A/B/C documentados no README.
- Baseline/orçamento: qualquer medição futura de câmera usa o pack M01 (`docs/benchmarks/m01/`) e o mesmo hardware/procedimento.
