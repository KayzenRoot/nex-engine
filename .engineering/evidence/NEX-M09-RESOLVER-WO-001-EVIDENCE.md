# Evidence Bundle · NEX-M09-RESOLVER-WO-001 (Preset resolver)

**Status:** `PROTOTYPE_EVIDENCE / PLANNING_ONLY / NO_RUNTIME_APPLICATION / NO_PERFORMANCE_CLAIM`
**Issue:** #14 · **Base:** `ec7048ff0c52671d2fb4d6b8e84aaf15ac9fef5d` · **Code SHA:** `bb320b3cd6f06ee355405b4d193348576081cc93`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/tools/preset_resolver/`: projeto Godot autocontido com `preset_resolver.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_preset_resolver.py`: 9 testes estruturais (arquivos/projeto, API, vocabulário `preset_pack.v1`, status/erros, ausência de aplicação runtime, marcador/evidência, limites, ausência de claim de performance).

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/tools/preset_resolver `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M09_RESOLVER_SMOKE_PASS: 50 checks`** (exit 0), log em `nex_modules/tools/preset_resolver/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 50 checks:
- configuração de hardware/Godot/contratos e rejeição de valores inválidos;
- carga do pack: schema, preset ids, tiers padrão únicos, settings não vazios, ranges/enums, reduced motion, monotonicidade de tier, versões de contrato e hardware;
- resolução por tier/id, valores de render/luz/performance, preset custom com reduced motion e warnings;
- overrides: merge profundo, caminho aplicado, manutenção de chaves irmãs e outros blocos, rejeição de bloco/valor inválido;
- reduced motion: rejeição sem escala e resolução com shake 0.25/hit-stop 0.5;
- incompatibilidade de hardware, contratos e faixa Godot;
- determinismo, último resultado e `clear()`.

## O que não foi feito / não é alegado

- Nenhum preset aplicado a `ProjectSettings`, engine, `project.godot`, cena ou renderer.
- Compatibilidade usa versões declaradas, não hardware probado.
- Qualidade visual/performance não validadas; `target_fps` é alvo.
- Nenhum claim de FPS, frame-time ou qualidade.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover `nex_modules/tools/preset_resolver/**`, `tests/ci/test_preset_resolver.py`, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Aplicação real de presets exige WO de runtime/engine com medição.
- M11/M12 permanecem não admitidos.
