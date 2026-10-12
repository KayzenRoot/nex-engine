# Checkpoint Delta — PROPOSTO, não canônico

**Estado:** `PROPOSED_ONLY_NOT_PROMOTED`
**PR:** #105
**Base main observada:** `a71df4c141ac52cc59778dc0f08831458d62ef33`
**HEAD de código/runtime validado:** `ea94eb98666966ce8c376df436dbfdd33c6da06f`
**Correção de portabilidade:** `9c17fc5b763619ef230f8f89a6bfb6b66a3b4518`
**Evidence Bundle original:** `016a620ccbf09293bf0950165f37458e6bf3e9f8`
**Uso:** proposta documental anexada à PR; ler o HEAD atual diretamente da PR antes de qualquer ação posterior.

## Texto proposto para anotação futura

> A validação gráfica Windows local do Visual Lab foi executada com Godot 4.7.2 oficial e RTX 5050 no código de produto `ea94eb98666966ce8c376df436dbfdd33c6da06f`. F1–F4, câmera, B/N/D e heatmap passaram; cinco amostras F10 (25/50/100/200 geometry e 25 combined) foram validadas. A leitura F10 está limitada por VSync e não é GPU frametime. A correção de line endings Windows no verificador e teste passou nas suítes locais. O bundle e checks associados estão anexados à PR #105.

## Restrições para qualquer promoção futura

- Este arquivo **não** altera `.engineering/CHECKPOINT.md`, JSON, Source Pack ou ledger; não é autoridade canônica e não aprova merge.
- Não declarar a PR integrada nem promover checkpoint enquanto a auditoria independente do HEAD exato e a autorização do owner não ocorrerem.
- Não admitir M01 ou outro módulo com base apenas nesta validação local. Qualquer futura atualização deve usar o SHA da `main` pós-merge e os checks exigidos nesse SHA, após autorização aplicável.
- O commit que inclui este próprio delta muda o HEAD documental; a auditoria deve consultar o SHA remoto atual e os checks exatos desse SHA, não presumir que os hashes acima são o HEAD final.

**Status proposto:** evidência técnica local anexada; revisão independente do HEAD atual pendente; merge e promoção de checkpoint não autorizados nesta execução.
