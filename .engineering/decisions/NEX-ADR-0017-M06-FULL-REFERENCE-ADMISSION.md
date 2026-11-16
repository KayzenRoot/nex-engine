# NEX-ADR-0017 · Admissão full reference do M06 e laboratório de performance

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-16
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `c763319d04d0bf353c15db8378872bdf8fab1734`

## Contexto

O Owner autorizou construir a NEX Engine de forma contínua e autônoma, finalizando os módulos base com rendering/runtime real. O M06 já tinha contrato `performance.v1`, atlas derivado de M09, 162 observações e advisories, mas não tinha laboratório nativo, planners executáveis nem evidência própria de instancing, LOD, culling, streaming, frame pacing, VRAM e fillrate.

## Decisão

Admitir, de forma **full reference e bounded ao M06**:

- **Bottleneck Atlas:** classificação CPU/GPU/pacing de 33 runs nativos do laboratório M06.
- **BatchWeave:** planner espacial e construção MultiMesh; comparação individual/multimesh/batched em três cenas.
- **LOD Governor:** seleção de detalhe por distância com histerese; comparação high/governor e diff visual.
- **Occlusion Mapper:** classificador frustum/AABB por câmera; teste ON/OFF e decisão conservadora sobre oclusão real.
- **StreamGuard:** carregamento assíncrono com estados, cache, duplicidade e falha; smoke de três cenas.
- **FramePacer:** política de render scale com histerese/cooldown; capturas estáticas 1.0/0.85/0.70 e diff visual.
- **VRAM Sentinel:** monitores de memória do engine e política de histerese; carga de 22 texturas e delta observado.
- **FillRate X-Ray:** proxy determinístico de overdraw e matriz 1/10/100 eventos × 720p/1080p/1440p.
- **R&D/QA:** matriz GO/NO_GO, relatório e gate; fechamento de #59–#68 e #11 após squash protegido.

## Escopo de arquivos admitido

- `nex_bench/scenes/m06_performance/**` (planners, smokes e laboratório nativo).
- `nex_bench/scenes/preset_ab/preset_ab.gd` (flags M06 e métricas de draw calls).
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-16-m06/**`.
- `docs/benchmarks/m06/**` e `tests/ci/test_m06_final.py`.
- Enforcement de builders e workflow CI.

## Exclusões explícitas

- Nenhuma alteração no renderer core, GDExtension, Godot fork ou `project.godot`.
- Nenhuma implementação de LOD engine de produção; o governor é um experimento bounded.
- Nenhuma oclusão real com occluders baked; o resultado é `INCONCLUSIVE_NOT_BAKED`.
- Nenhum render scale dinâmico por frame, shader prewarm ou eviction de VRAM.
- Nenhum streaming de cena, prefetch de disco ou orçamento global entre módulos.
- Nenhum claim de FPS generalizado, qualidade cross-device, jogo ou paridade com PoE2.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. `build_m06_runtime.py --check`, builders M06 existentes e validadores de evidência reproduzem os artefatos.
3. Smokes M06 `78 + 17 + 9` checks PASS; 33 runs validados.
4. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
5. M07–M12 continuam bounded e exigem WO própria.
6. O fechamento de issues só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M06 passa a ser o sexto módulo base concluído como **performance de referência**, não como jogo.
- M07/M08/M09 podem consumir as medições; M11 pode auditar as técnicas e limitações.
- MultiMesh e LOD mostram ganho mensurável; o mapper de frustum customizado é rejeitado por falta de ganho e risco visual.
