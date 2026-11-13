# Evidence Bundle · NEX-M04-TEXTUREBUDGET-WO-001 (Texture-budget planner)

**Status:** `PROTOTYPE_EVIDENCE / PLANNING_ONLY / NO_DECODING / NO_ATLAS_PACKING / NO_VRAM_CLAIM`
**Issue:** #9 · **Base:** `65afc09666f8e8f5046e471c8a8e37cf71368279` · **Code SHA:** `658ee86f70fea867db1cac0ad46a178d4b350cc0`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/materials/texturebudget/`: projeto Godot autocontido com `texture_budget_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_texture_budget_planner.py`: 9 testes estruturais (arquivos/projeto, API, vocabulário `material.v1`, vereditos/achados, ausência de decoding/rendering, marcador/evidência, limites, ausência de claim de VRAM).

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/materials/texturebudget `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M04_TEXTUREBUDGET_SMOKE_PASS: 55 checks`** (exit 0), log em `nex_modules/materials/texturebudget/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 55 checks:
- configuração de bytes/count/atlas, rejeição de limites e restauração;
- conjunto vazio, contagem de materiais/referências, deduplicação por SHA-256 e bytes economizados;
- fórmula de bytes com e sem mips (1024×1024 sem mips = 4 MiB);
- orçamento de bytes excedido, plano de downscale, projeção dentro do orçamento e ordem do maior texture;
- orçamento de contagem, veredito `TIGHT`, pressão de atlas e recomendação de atlas;
- achados: oversized, non-power-of-two, sRGB em normal/ORM, mips ausentes e mismatch de digest/dimensões;
- validação de material id (padrão do contrato), slot, SHA, dimensões e booleanos; `INVALID_INPUT` com razão;
- determinismo, último relatório e `clear()`.

## O que não foi feito / não é alegado

- Nenhuma textura carregada, decodificada, enviada à GPU ou empacotada; nenhum `Image`/`Texture2D`/`ResourceLoader`.
- Bytes decodificados são aritmética (`w*h*4`, fator 4/3 com mips), não VRAM real.
- Pressão de atlas é contagem de tiles de 256 px, não simulação de allocator/packer.
- Downscale é sugestão de planejamento; nenhuma reamostragem ou validação visual.
- Performance/qualidade: `INCONCLUSIVE_NOT_RUN`.
- M04 parent (#9) permanece `NOT_ADMITTED`.

## Rollback

Remover `nex_modules/materials/texturebudget/**`, `tests/ci/test_texture_budget_planner.py`, este bundle, o delta e a WO/lock correspondentes. Nenhum estado de engine, contrato ou checkpoint é alterado.

## Próximos passos

- Validação real de texturas exige WO de import/decode/atlas com GPU.
- M05 FX budget e demais submódulos exigem WO própria.
