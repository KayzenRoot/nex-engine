# Evidence Bundle · NEX-M10-CONTRACT-WO-001 (Combat feedback contract v1)

**Status:** `CONTRACT_ONLY / NO_ANIMATION / NO_GAME_FEEL_CLAIM / NOT_MODULE_ADMISSION`
**Issue:** #15 · **Base:** `f0f5bec11ca859a74eb3c6964e923728b4c552ed` · **Code SHA:** `97c80641075ec14068c59af1abae529f8ef4c6b5`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `contracts/m10/feedback.v1.schema.json`: fases do ataque, hit events, canais (hit-stop, shake, flash, recoil, damage number), prioridade/intensidade, orçamento de hit-stop/shake/concorrência/total, performance e proveniência.
- `contracts/m10/ownership.v1.json`: ownership prospectivo de `nex_modules/animation/**`.
- `docs/contracts/m10.md`: invariantes, janela + tail, validação, ownership e compatibilidade.
- `tests/contracts/test_m10_feedback_contract.py`: 20 testes.

## Invariantes verificados

- Fases únicas, `active` obrigatória, duração total ≤ 10000 ms.
- IDs de evento/canal únicos; evento dentro do ataque; `critical` exige dano > 0.
- Canal inicia dentro do ataque e termina no máximo 1000 ms depois; `event_id` referenciado existe.
- `damage_number` exige evento com dano > 0.
- Hit-stop ≤ `max_hit_stop_ms`; shake ≤ `max_shake_amplitude`; total ≤ `max_total_channels`; concorrência ≤ `max_concurrent_channels`.
- Performance `MEASURED`/`UNAVAILABLE` coerente; proveniência exige evidência quando medida; FPS rejeitado.

## Verificação executada

```powershell
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
```

Resultado: **150 testes OK** (130 preexistentes + 20 novos).

## O que não foi feito / não é alegado

- Nenhuma animação, hit-stop, shake, flash, recoil, damage number, câmera ou rendering implementado.
- Nenhum claim de game feel, legibilidade, FPS ou frame-time.
- M10 parent (#15) permanece `NOT_ADMITTED`; contratos M01–M08 inalterados.

## Rollback

Remover `contracts/m10/**`, `docs/contracts/m10.md`, o teste novo, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Planejador de feedback e integração em combate exigem WO própria.
- M11/M12 permanecem não admitidos.
