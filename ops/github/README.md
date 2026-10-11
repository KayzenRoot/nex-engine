# Nex Engine | GitHub Ruleset e proteção de main

**Status: PREPARAÇÃO, NÃO APLICADA**. A integração ChatGPT pode criar arquivos/PRs, mas não tem operação de escrita de Rulesets; a leitura do endpoint legado de proteção da branch main retornou 403. Isto NÃO confirma nenhuma regra ativa.

**Desired:** main sob PR obrigatório, squash-only, linear history, bloqueio de force push e exclusão, resolver conversas; checks CodeRabbit e os dois Socket Security; strict up-to-date. Sem bypass. Aprovação formal 0 nesta fase de proprietário individual, mas auditoria ChatGPT/Owner, review CodeRabbit e checks são obrigatórios. Jobs GEF CI só devem entrar no Ruleset depois de existirem e passarem no PR.

**Dry run local PowerShell**: powershell -ExecutionPolicy Bypass -File ops/github/apply-nex-main-protection.ps1

**Aplicação**: somente após a PR #72 estiver MERGED, com CodeRabbit SUCCESS e Socket verdes no último HEAD revisado, além de permissão admin autenticada em gh CLI. Comandos: gh auth status --hostname github.com; powershell -ExecutionPolicy Bypass -File ops/github/apply-nex-main-protection.ps1 -Apply . Fazer login interativo apenas se Owner autorizar; nunca divulgar PAT.

O script lê repo/PR72/checks, PATCH de configurações gerais squash-only, POST ou PUT do Ruleset com nome gerenciado, e GET de validação; se qualquer condição falhar, para. Não modifica outros repositórios.

**Próximo arquivo:** docs/operations/NEX-CODEX-DESKTOP-START.md tem prompt completo para executar bootstrap GEF em Windows LOCAL depois de governança promovida, com evidence/CI e STOP conditions. Não instalar/aplicar às cegas.
