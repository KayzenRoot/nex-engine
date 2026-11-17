# NEX M09 · Editor tools

**Status:** `M09_EDITOR_TOOLS_REFERENCE_DERIVED / HEADLESS_FIXTURES / NO_IMPORT_OR_RENDER / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `371ca4ab4a5f70debc96e84bba55aba3870fc9cf` · **Engine:** Godot 4.7.2-stable

## S01 · PresetResolver

- **PRESET_RESOLVER_VERIFIED**: 50 checks headless.

## S02 · PerfLint

- **PERFLINT_DERIVED**: 42 checks; 13 findings (4 errors, 9 warns); highest `error`.

| Código | Ocorrências |
|---|---:|
| alpha_overdraw_risk | 1 |
| draw_call_budget_exceeded | 1 |
| duplicate_id | 1 |
| invalid_dimensions | 1 |
| light_budget_exceeded | 1 |
| missing_license | 1 |
| missing_scene_id | 1 |
| oversized_file | 1 |
| shadow_budget_exceeded | 1 |
| sync_load_risk | 2 |
| texture_too_large | 1 |
| unknown_format | 1 |

## S03 · ImportGuard

- accepted **1**, rejected **3**, noop **2**, conflicts **1**.
- Plano determinístico; nenhum arquivo é escrito ou sobrescrito.

## S04 · BenchmarkRecipe

- Recipe `m09-corridor_static-ab-high-4101`; scene `corridor_static`, preset `ab-high`, seed `4101`, driver `vulkan`, runs `3`.

## S05 · QA

- 92 checks totais; 4 fixtures; 0 assets de terceiros.

## Decisões

| Tecnologia | Decisão | Evidência |
|---|---|---|
| PresetResolver / preset_pack.v1 | **GO** | 50 headless checks; no runtime application |
| PerfLint | **GO_WITH_LIMITATIONS** | 42 checks; 13 deterministic findings (4 errors, 9 warns) |
| ImportGuard | **GO_WITH_LIMITATIONS** | 1 accepted / 3 rejected / 2 noop / 1 conflict; plan only, no writes |
| BenchmarkRecipe | **GO_WITH_LIMITATIONS** | recipe generated and validated; no benchmark executed |

## Observações

- PresetResolver still passes 50 headless checks
- PerfLint reports 13 deterministic findings: 4 errors and 9 warnings
- ImportGuard plans 1 accepted, 3 rejected, 2 noop and 1 conflict without writing files
- BenchmarkRecipe builds a reproducible recipe with pinned driver and source SHA
- all editor tools run headless with deterministic fixtures

## Limitações

- fixtures only; no asset is imported, rendered or benchmarked
- PerfLint warnings are heuristics, not measured performance
- ImportGuard never writes; the real import pipeline remains future work
- no FPS, frame-time, VRAM or quality claim
- no production art, no PoE2 parity and no generalized claim

Gerado por `docs/benchmarks/m09/tools/build_m09_editor_tools.py`; não é benchmark de jogo.
