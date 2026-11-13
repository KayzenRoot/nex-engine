# NEX M01 · Desvios do plano

| ID | Desvio | Justificativa/estado |
|---|---|---|
| D-01 | S04 Run9 terminou `INVALID`; 200g ficou 2/3 | Retomada autorizada adicionou 1 run; matriz final 3/3. Causa do Run9 não determinada. |
| D-02 | Negativo de resize não exercitável | `stretch/mode=canvas_items` fixa o viewport; captura diagnóstica comprova. Aceito pelo Owner. |
| D-03 | S05 em sessão única, 1 rep/célula | Limitação de tempo/GPU; baseline-25 ×3 para variabilidade. Declarado em todos os artefatos. |
| D-04 | Validador S05 delega ao canônico após validar a cena | Evita duplicar regras; o v2 rejeita a cena por design. Fronteira testada e documentada. |
| D-05 | Sem runs 1080p | Baseline em 1280×720/VSync; metas 1080p60/120 permanecem aspiracionais. |
| D-06 | Sem Docker/cloud GPU | Windows nativo é a única fonte válida; CI headless não é benchmark. |
| D-07 | QA-FINDING-001 corrigido fora do escopo original de QA | Correction WO separado (PR #122) com teste endurecido. |
| D-08 | Hashes históricos divergem em checkout CRLF | Export byte-exato comprova 18/18; configuração local não alterada. |
| D-09 | Audit pack referencia artefatos em vez de copiá-los | `manifest.json` guarda caminho + SHA-256; evita duplicação de ~5 MB e mantém verificação byte-exata. |
