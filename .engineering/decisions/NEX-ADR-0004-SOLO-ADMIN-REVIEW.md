# NEX-ADR-0004 | Execução e auditoria solo pelo administrador

**Status:** OWNER_APPROVED_ON_PROMOTION (2026-11-13)  
**Work Order:** NEX-GOV-SOLO-WO-001, Issue #108  
**Autoridade:** diretiva expressa do Owner em 2026-11-13. Eficaz após PR de governança protegida, CI e merge.  
**Âmbito:** todas as próximas WOs da NEX Engine, sem alterar o escopo de produto de uma WO já admitida.

## Decisão

A NEX Engine é desenvolvida por um único administrador, usando Codex Desktop e ChatGPT como executores e auditores técnicos. **Nunca exigir revisor humano independente, colaborador externo, convite a revisor ou aprovação de pessoa de fora do projeto** como pré-condição de execução, revisão técnica, PR, squash ou merge.

O administrador pode executar e auditar o próprio trabalho. A auditoria será objetiva, vinculada a BASE_SHA/HEAD_SHA, diffs, testes e Evidence Bundle, identificada honestamente como `ADMIN_SOLO / NOT_INDEPENDENT`. Nenhum executor deve fingir que isso equivale a um review humano independente. Checks automáticos ou análise de múltiplas ferramentas não são revisores humanos.

A ausência de revisores externos **não dispensa**:
- branch/PR, squash protegido, histórico linear e regras de exclusividade de arquivos e GPU;
- todos os status checks obrigatórios da `main` (Governance, Fast Lane, Free Review, SonarCloud e Socket x2), mais CodeQL, builds/testes específicos e análise de arquitetura/segurança apropriados;
- conferência de diff, fingerprint, BASE/HEAD imutáveis, ausência de threads pendentes e integridade das evidências;
- bloqueio de regressões conhecidas HIGH/CRITICAL, migrações inseguras, perdas de dados ou benchmarks fabricados;
- Context Lock, Work Order admitida, definição de pronto, revisão de risco e checkpoint somente após verificação pós-merge;
- veto a `force-push`, reset destrutivo, bypass de regras, merge com CI incompleta e acesso indevido a segredos.

## Política de merge sem pausa por revisor

Para WOs **já admitidas**, o Owner delega permanentemente ao fluxo de administrador solo o squash de PRs LOW/STANDARD após: execução e evidência concluídas, análise técnica solo registrada, seis checks de proteção completos/verde no HEAD exato, ausência de defeitos HIGH/CRITICAL, verificação do HEAD/base imediatamente antes da operação e revisão pós-merge. **Não exigir uma segunda pessoa ou uma nova aprovação de review humano**.

Para risco ELEVATED ou HIGH_ASSURANCE, exigem-se provas técnicas adicionais, testes de recuperação e uma decisão documentada do administrador sobre riscos e operações irreversíveis. Essa decisão **não exige outra pessoa**, mas um bloqueio de segurança não é resolvido por autoaprovação. Em especial, dinheiro, signing, privilégios, segredos, perdas de dados e APIs incompatíveis nunca avançam apenas com CI verde.

Se regras de plataforma realmente exigirem aprovação humana, registrar `BLOCKED_PLATFORM_REVIEW_REQUIREMENT` e corrigir a configuração somente mediante permissão administrativa, sem bypass. O ruleset #24864413 foi inspecionado em 2026-11-13: `required_approving_review_count=0`, `required_reviewers=[]` e `require_code_owner_review=false`; portanto nenhuma mudança no ruleset foi necessária para o squash da PR #107.

A permissão para auditoria solo **não admite automaticamente** as 66 issues de planejamento M02–M12, não permite executar módulos com dependências ausentes, e não promete execução assíncrona fora de uma sessão ativa. O executor prossegue em WOs NECESSARY admitidas, usando Context Lock renovado após mudança canônica, e interrompe apenas por STOP técnico/autorização de ação irreversível realmente exigida.

## Compatibilidade com decisões anteriores

Esta ADR substitui **somente as cláusulas de obrigatoriedade de revisor humano externo/independente** em decisões, issues, templates, WOs ou checkpoints históricos. Mantém integralmente as obrigações de evidência, teste, risco, separação de escopo e proteção da `main` do NEX-ADR-0002 e do Source Pack. Textos antigos continuam como histórico e não podem ser interpretados como imposição de revisor externo.

## Exemplo auditado

A PR #107 foi integrada por squash protegido em `4d69b7bd264f4814317c6e5fe98eaccdc2b620e0`, após 13/13 checks e auditoria `NOT_INDEPENDENT`. A matriz RTX5050 reuniu 12/12 capturas `COMPLETE` com fonte medida `d59c94da...`; há duas limitações expressas: redimensionamento não exercitável sob `canvas_items` e dados de pacing não comparáveis entre sessões de ~75 e ~60 callbacks/s. Isso **não** certifica o projeto inteiro nem o parent M01.

## Critérios de promoção

Issue #108; PR com diff estritamente documental e checks obrigatórios íntegros; auditoria solo referenciada por SHA; squash normal; validação de CI da `main` pós-merge e reconciliação canônica sem declarações não provadas.
