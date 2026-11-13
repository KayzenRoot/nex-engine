# Evidence Bundle · NEX-M02-S02-WO-001 (Sightline prototype)

**Status:** `PROTOTYPE_EVIDENCE / NO_ENGINE_INTEGRATION / NO_SHADER_CHANGE / NO_PERFORMANCE_CLAIM`
**Issue:** #29 · **Base:** `a50675bb21cb2a9519e76ec5b4a68c2f4e146d3f` · **Code SHA:** `6057c1da576458767f39d5dd5328ad763da3931d`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/render3d/sightline/`: projeto Godot autocontido com `sightline_controller.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_sightline.py`: 9 testes estruturais (arquivos, projeto, API, enums, histerese/visibilidade separada, ausência de atalho de rendering, marcador/evidência, política/limites, ausência de claim fabricado).

## Verificação executada

Comando (Godot oficial 4.7.2, binário `ab1824f8…`):

```powershell
& "<pinned Godot>" --headless --path nex_modules/render3d/sightline `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M02_S02_SMOKE_PASS: 49 checks`** (exit 0), log em `nex_modules/render3d/sightline/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 49 checks:
- interseção segmento–AABB (hit, miss, atrás do jogador, dentro de volume amplo);
- validação de configuração/registro (duplicata, tamanho zero, alpha/distância inválidos);
- jogador atrás de muro: gameplay bloqueado, reveal após delay, silhueta, alpha 1;
- vegetação: fade para `target_alpha`, sem silhueta;
- decoração: sem reveal, oclusão do mundo preservada;
- ameaça crítica: `danger_alert` imediato, `critical_unseen` durante delay, reveal depois;
- ameaça além da distância crítica: alerta sem silhueta/reveal forçado;
- occluder transparente: gameplay visível, sem reveal;
- cap de reveals: exatamente um ativo, outro `capped`;
- histerese: jitter de 10 ciclos sem flicker;
- parede móvel: saída limpa, progresso 0, silhueta limpa;
- câmera movida: sightline muda, gameplay volta a visível;
- muro atrás do jogador: sem silhueta indevida;
- determinismo: duas sequências idênticas produzem estado JSON idêntico.

## O que não foi feito / não é alegado

- **Cenas reais** (`corridor_static`, `arena_combat`, `dense_city`) não executadas; o protótipo usa AABBs mock.
- **Performance/frame-time/VRAM: `INCONCLUSIVE_NOT_RUN`.** Nenhum rendering; nenhum número inventado.
- Sem shader/material/engine change; sem integração com `nex_bench`.
- AABB-only; vegetação/VFX reais e portas móveis exigem WO de integração de cena.
- Ordenação do cap por distância câmera→centro do AABB; um muro alto próximo da câmera pode prevalecer sobre um muro baixo próximo do jogador. Comportamento documentado e testado pelo invariante, não por id.

## Rollback

Remover `nex_modules/render3d/sightline/**`, `tests/ci/test_sightline.py`, este bundle e o delta. Nenhum arquivo do M01, câmera S01, contratos, CI ou checkpoint é alterado.

## Próximos passos

- M02-S03 (DepthWeave) pode consumir a política/estado como mock.
- Integração real em cenas e materiais exige WO própria e contrato de materiais (M04) quando admitido.
- Qualquer medição de frame-time deve usar o baseline M01 e o mesmo hardware/procedimento.
