# Evidence Bundle · NEX-M10-FEEDBACK-WO-001 (Combat-feedback planner)

**Status:** `PROTOTYPE_EVIDENCE / PLANNING_ONLY / NO_ANIMATION / NO_RENDERING / NO_GAME_FEEL_CLAIM`
**Issue:** #15 · **Base:** `9b88b7abc1cc6b5ce13551a915a4cb6311ec65eb` · **Code SHA:** `e62d9290cf0d96008823cab84c62cb0da21d9425`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/animation/combat_feedback/`: projeto Godot autocontido com `feedback_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_feedback_planner.py`: 9 testes estruturais (arquivos/projeto, API, vocabulário `feedback.v1`, vereditos/achados, ausência de animação/rendering, marcador/evidência, limites, ausência de claim de game feel).

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/animation/combat_feedback `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M10_FEEDBACK_SMOKE_PASS: 66 checks`** (exit 0), log em `nex_modules/animation/combat_feedback/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 66 checks:
- configuração de budgets (hit-stop/shake/concorrência/total) e limites;
- ataque: id, fases, active obrigatória, duplicata, duração total;
- hit events: id/tempo/target/dano/elemento, duplicata e cap;
- canais: id/tipo/start/duração/intensidade/prioridade/referência, duplicata e cap;
- plano seguro: timeline ordenada, 5 canais, duração 400 ms, pico de concorrência 5, hit-stop 60 ms, shake 0.4, 1 damage number, determinismo;
- conflitos: evento fora do ataque, crítico sem dano, canal fora da janela+tail, evento pendente, damage number sem dano, hit-stop/shake/total/concorrência acima do budget;
- estados inválidos: sem ataque, sem canais;
- exportação `feedback.v1` apenas para plano seguro, performance `UNAVAILABLE`, vocabulário de fases e campos exclusivos omitidos;
- exportação recusada com conflito; proveniência validada (SHA/status/evidence); `clear()`.

## O que não foi feito / não é alegado

- Nenhum `AnimationPlayer`, tween, câmera, shader, cena ou renderer criado.
- Hit-stop/shake são aritméticos; concorrência é por intervalo de início, não overlap renderizado.
- Prioridade ordena a timeline, mas não resolve conflitos automaticamente.
- Game feel/readability/runtime: `INCONCLUSIVE_NOT_RUN`.
- M10 parent (#15) permanece `NOT_ADMITTED`.

## Rollback

Remover `nex_modules/animation/combat_feedback/**`, `tests/ci/test_feedback_planner.py`, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Integração em combate real exige WO de cena/animação com medição.
- M11/M12 permanecem não admitidos.
