# NEX M09 · Preset A/B/A measurement stage

**Status:** `MEASUREMENT_HARNESS / ISOLATED_SCENE / NO_ENGINE_CHANGE / ADMIN_SOLO_NOT_INDEPENDENT`

Cena de medição autocontida para comparar dois presets `preset_pack.v1` no mesmo workload, usando o profiler de GPU existente. Não altera `project.godot`, `hub.gd`, renderer, shaders ou CI.

## Workload

- 200 proxies determinísticos, luz direcional e 4 omni lights.
- Câmera isométrica fixa, 1280×720 por padrão.
- `effect_mode: lights`, `proxy_count: 200` (contrato v2 do profiler).
- VSync desligado e `max_fps = 240` para evitar o cap de 16k amostras.

## Presets

| Preset | Scale | MSAA | Shadows | Atlas | Glow |
|---|---:|---|---|---:|---|
| `ab-low` | 0.5 | off | low | 1024 | off |
| `ab-high` | 1.0 | 4x | ultra | 4096 | on |

## Execução

```powershell
$env:NEX_GPU_PROFILE_SOURCE_SHA = "<40-hex commit>"
$env:NEX_PRESET_AB_AUTORUN = "1"
$env:NEX_PRESET_AB_PRESET = "ab-low"
& "<pinned Godot 4.7.2>" --path nex_bench --rendering-method forward_plus `
  res://scenes/preset_ab/preset_ab.tscn
```

O processo imprime `NEX_PRESET_AB_CAPTURE <path>` e encerra. Repita com `ab-high` e depois `ab-low` para o A/B/A.

## Validação

```powershell
Get-Content -Raw <capture>.json | python nex_bench/scenes/preset_ab/validate_preset_ab.py
```

O validador confere cena/layout/proxy/effect/max_fps/vsync e delega todos os agregados ao validador canônico.

## Limitações

- Sessão sintética única; uma repetição por preset (A/B/A dá duas amostras de A).
- Sem generalização entre cenas, drivers, hardware ou sessões.
- `max_fps = 240` limita o pacing; a comparação principal é GPU p95/p99 e 1% low.
- O harness aplica um subconjunto de `preset_pack.v1` (resolução, MSAA, sombras, atlas, glow, tonemap, target fps); não é o resolvedor completo.
- Nenhum claim de FPS de jogo ou ganho universal.
