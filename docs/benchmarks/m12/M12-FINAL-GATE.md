# NEX M12 · Final brand-system gate

**Status:** `M12_BRAND_SYSTEM_REFERENCE_COMPLETE / DISTRIBUTION_TRADEMARK_PENDING / OWNER_AUTHORIZED / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-17 · **Base:** `c2c13c57b4de7a5114db2e2b79d37a7e026bfa62`
**Parent:** #17.

## O que foi concluído

| Área | Entrega | Evidência |
|---|---|---|
| Wordmark | NEX ENGINE em paths outline, sem fonte | `wordmark.svg`, `logo-primary.svg` |
| Paleta | 5 tokens canônicos e contraste | `palette.v1.json`, `brand-kit.v1.json` |
| App icons | 9 PNGs + ICO + ICNS | `assets/brand/app-icons/` |
| UI icons | 10 ícones 24×24 `currentColor` | `assets/brand/icons/` |
| Identidade | `identity.v1` com hashes e thresholds | `identity.v1.json`; 14 checks |
| QA | Smoke headless, relatório e gate | `m12-final-identity-2026-11-17.json`; este gate |

## Resultado

- **Wordmark:** outline geométrico; nenhum `<text>` ou `font-family`; viewBox `0 0 190 100`.
- **Paleta:** 5 tokens; Mist/Graphite **16.48:1**; Cobalt/Graphite **4.27:1**; Cyan **10.63:1**; Amber **10.51:1**.
- **App icons:** **9** tamanhos (16–1024); ICO **47845 bytes** com 9 entradas; ICNS **45394 bytes** íntegro.
- **UI icons:** **10** ícones 24×24 com `currentColor`.
- **Identidade:** `identity.v1` **READY_FOR_UI**, **0 findings**, **14 checks** no smoke final.
- **Builder:** `M12_BRAND_KIT_CHECK_PASS: 9 sizes / 10 icons`.

## Limitações

- Nenhuma integração com editor UI, launcher, installer, hub, renderer ou binário da engine.
- Nenhuma alteração em `nex_bench/project.godot`, cenas de produção ou ícones do editor.
- Licença de distribuição e clearance de trademark permanecem **DISTRIBUTION_TRADEMARK_PENDING**.
- Contraste é calculado dos hex declarados, não medido em tela.
- Nenhum asset, fonte, shader ou marca de terceiros; a marca não deriva do logo Godot.
- **Nenhuma paridade com PoE2 é alegada.**
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Fechamento

Com este gate, a issue **#17** pode ser fechada como `COMPLETED` após o merge protegido e os checks pós-merge. O sistema de marca está pronto para uma futura UI, mas nenhuma UI, launcher, installer ou rebranding de binário é admitido por este gate.
