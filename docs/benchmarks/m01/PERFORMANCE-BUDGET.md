# NEX M01 · Orçamento de performance (proposta)

**Status:** `PROPOSED_PENDING_OWNER_APPROVAL` · **Não é meta atingida nem autorização de implementação.**
Fonte mecânica: [`budget.v1.json`](budget.v1.json) · Base: [`manifest.json`](manifest.json) e [`BASELINE.md`](BASELINE.md).

## Como os tetos foram derivados

1. Medição nativa Windows/RTX 5050, Forward+/Vulkan, 1280×720, VSync 1.
2. Cada teto é o valor medido no baseline **mais 25–35% de folga**, arredondado para cima.
3. Nenhum teto usa dados de CI headless, Docker ou sessão diferente.
4. Medições de uma sessão (S05) e matriz S04; repetições e variabilidade declaradas no baseline.

| ID | Cenário | Medido | Teto proposto |
|---|---|---:|---:|
| s04-baseline-200g-gpu-p95 | S04 200 geometry, GPU p95 | 0,295 ms | 0,40 ms |
| s05-baseline-200g-gpu-p95 | S05 baseline 200, GPU p95 | 0,218 ms | 0,30 ms |
| s05-lights-200g-gpu-p95 | S05 4 omni lights 200, GPU p95 | 0,321 ms | 0,45 ms |
| s05-shadows-200g-gpu-p95 | S05 sombras 200, GPU p95 | 0,547 ms | 0,75 ms |
| s05-vfx-200g-gpu-p95 | S05 4 emitters 200, GPU p95 | 0,261 ms | 0,36 ms |
| s05-combined-25-gpu-p95 | S05 combined 25, GPU p95 | 1,194 ms | 1,60 ms |
| pacing-p95 | Pacing p95 em qualquer run auditado | 17,25 ms | 18,0 ms |
| one-percent-low | 1% low derivado do pacing | 52,66 | ≥ 50,0 |
| fresh-session-allocation-delta | Alocação do renderer, sessão nova | histórico 48→125 MiB | +15% vs baseline |

## Metas aspiracionais (não medidas)

| Meta | Orçamento de frame | Status |
|---|---:|---|
| 1080p Quality 60 FPS | 16,7 ms | `ASPIRATIONAL_NOT_MEASURED` |
| 120 FPS Performance (experimental) | 8,3 ms | `ASPIRATIONAL_NOT_MEASURED` |

Os runs atuais são 1280×720 com VSync; portanto **nenhuma meta de FPS foi atingida ou alegada**. O laboratório é o instrumento; a meta é decisão futura de módulo.

## Regras de aplicação

- Um módulo futuro (M02–M06) só pode comparar contra este baseline no **mesmo** hardware/driver/renderer/viewport/VSync e com o mesmo procedimento (2 s + 30 s, 3 repetições).
- Comparação entre sessões com taxa de callbacks diferente (~75 vs ~60) é inválida; declarar `INCONCLUSIVE`.
- `RENDERER_ALLOCATION_BYTES` não é VRAM; orçamento de VRAM exige fonte de dispositivo separada e atribuição explícita.
- Tetos são gates de revisão, não permissão de merge; cada módulo exige WO e aceitação própria.
- Qualquer aumento de teto exige decisão registrada do Owner com justificativa medida.
