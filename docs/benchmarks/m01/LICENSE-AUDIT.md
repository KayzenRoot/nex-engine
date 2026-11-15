# NEX M01 · Auditoria de licenças e proveniência de assets

**Status:** `ORIGINAL_NEX_GENERATED_NO_THIRD_PARTY_ASSETS / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-15 · **Base:** `900d2b2d031a87048702625a1e98bc50905bc663`

## Escopo

As três cenas de referência M01 e os recursos diretamente usados pelo laboratório visual:

| Recurso | SHA-256 | Recursos externos | Proveniência |
|---|---|---:|---|
| `nex_bench/scenes/base/corridor_static.tscn` | `9fada790…` | 0 | Geometria e materiais originais NEX, primitivas Godot |
| `nex_bench/scenes/base/arena_combat.tscn` | `13f6e1a3…` | 0 | Geometria e materiais originais NEX, primitivas Godot |
| `nex_bench/scenes/base/dense_city.tscn` | `429e3a17…` | 0 | Geometria e materiais originais NEX, primitivas Godot |
| `nex_bench/scenes/base/viewer.tscn` + `viewer.gd` | — | 1 script local | Código original NEX |
| `nex_bench/scenes/preset_ab/preset_ab.gd` | — | 0 assets | Código original NEX |
| `nex_bench/presets/preset_ab/presets.v1.json` | — | 0 assets | Dados originais NEX |
| `nex_bench/gpu_profile/session.gd` | — | 0 assets | Código original NEX |

## Resultado

- **0 assets de terceiros** referenciados pelas três cenas M01.
- **0 texturas, modelos, fontes, áudios ou SVGs externos** no caminho de captura.
- Os materiais das cenas são `StandardMaterial3D` com cores e parâmetros originais.
- O kit M04 (`nex_modules/materials/kit/**`) é procedural e original; **não** é usado pelas cenas M01 nesta admissão.
- Nenhuma licença de terceiro é invocada, portanto não há obrigação de atribuição externa para o laboratório M01.

## Limitações

- Esta é uma auditoria técnica de proveniência de arquivos, não uma opinião jurídica.
- A ausência de assets externos foi verificada por `[ext_resource]` nas cenas e pelo conteúdo dos recursos locais.
- A revisão é `ADMIN_SOLO / NOT_INDEPENDENT`; não há revisor jurídico independente.
- O kit M04 permanece com licenças `unverified` na auditoria M11; isso não afeta as cenas M01, que não o utilizam.
