# Evidence Bundle · NEX-M09-ATLAS-WO-001 (atlas de medições M09)

**Status:** `EVIDENCE_SYNTHESIS / SINGLE_SESSION / MEASUREMENT_CAMPAIGN_INDEXED / NO_GENERALIZATION`
**Issue:** #14 · **Base:** `a33655a1ea55508a2d24d688936348a42c9ef10c`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `docs/benchmarks/m09/measurement-atlas.v1.json`, `MEASUREMENT-ATLAS.md` e builder determinístico.
- Índice verificado dos oito bundles M09: 144 capturas de performance, 18 imagens, 330 arquivos de evidência e 8 source SHAs.
- `tests/ci/test_measurement_atlas.py`: 6 testes de contagens, source SHAs, valores-chave e reprodutibilidade.

## Bundles indexados

| Bundle | Tipo | Runs | Arquivos | Source SHA |
|---|---|---:|---:|---|
| preset-ab | performance | 6 | 15 | `baf818ef` |
| proxy-scaling | performance | 18 | 39 | `4e4719ac` |
| m01-ab | performance | 18 | 39 | `617db53d` |
| m01-visual | visual | 18 | 21 | `952b5a6` |
| res-scaling | performance | 18 | 39 | `6ebb98e8` |
| interaction | performance | 24 | 51 | `2ef072c7` |
| cross-scene | performance | 48 | 99 | `2a03cbb7` |
| interaction-200 | performance | 12 | 27 | `c1b73743` |

## Achados cross-experiment

- O preset high custa mais GPU que o low em todas as cenas e células medidas; o custo relativo cresce com a resolução.
- Em 50–200 proxies em `arena_combat`, a resolução domina o custo GPU; proxies afetam mais o CPU.
- O padrão de dominância de resolução se repete em `corridor_static` e `dense_city`.
- As capturas visuais A/A são byte-idênticas; A/B difere em 1.745–4.077% dos pixels a 1280×720.
- Tudo é sessão única em uma RTX 5050; sem generalização cross-device ou cross-session.

## Verificação

- O builder verifica contagem de runs, contagem de arquivos em `SHA256SUMS` e igualdade de source SHA entre relatório e manifesto para cada bundle.
- `build_measurement_atlas.py --check` reproduz o atlas.
- Os builders de todos os bundles continuam reproduzindo seus relatórios.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma nova captura, mudança de engine, cenas, `project.godot`, hub ou CI.
- Nenhum claim de FPS de jogo, qualidade visual, ganho universal ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover o atlas, o builder, o teste novo e o delta/WO/lock correspondentes.

## Próximos passos

- 2560×1440, outros hardwares, animação/temporal e integração no hub exigem WO própria e, no caso de integração, admissão do parent.
