# Stress index

| Workload | Caminho | Cargas | Evidência |
|---|---|---|---|
| S04 Density Ladder | `nex_bench/stress/density_ladder.gd` + evidências R9 | 25/100/200 geometry; 25 combined | 12/12 COMPLETE + Run9 INVALID |
| S05 Lighting Matrix | `nex_bench/scenes/lighting_matrix/` + evidências S05 | baseline, lights, shadows, vfx, combined-25 | 15/15 COMPLETE |
| Contratos | `contracts/m01/telemetry_run.v1.schema.json` | unidade/clock/availability | validado por CI |

Safe stop: workloads têm limites e cancelamento; nenhuma execução concorrente de GPU.
