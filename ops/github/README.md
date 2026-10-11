# Nex Engine | GitHub Ruleset e proteção de main

**Status: PREPARAÇÃO, NÃO APLICADA**. A integração ChatGPT pode criar arquivos/PRs, mas não tem operação de escrita de Rulesets; a leitura do endpoint legado de proteção da branch main retornou 403. Isto NÃO confirma nenhuma regra ativa.

**Desired:** main sob PR obrigatório, squash-only, linear history, bloqueio de force push e exclusão, resolver conversas; checks CodeRabbit e os dois Socket Security; strict up-to-date. Sem bypass. Aprovação formal 0 nesta fase de proprietário individual, mas auditoria ChatGPT/Owner, review CodeRabbit e checks são obrigatórios. Jobs GEF CI só devem entrar no Ruleset depois de existirem e passarem no PR.

**Dry run local PowerShell**: powershell -ExecutionPolicy Bypass -File ops/github/apply-nex-main-protection.ps1

**Aplicação**: somente após a PR #72 estar MERGED, com CodeRabbit SUCCESS e os dois checks Socket SUCCESS no HEAD revisado, e a PR #73 estar aprovada na auditoria Owner/Steward e MERGED, com CodeRabbit SUCCESS, os dois checks Socket e os dois jobs NEX Governance SUCCESS no seu HEAD exato. Exigir também permissão admin autenticada em gh CLI. Comandos: gh auth status --hostname github.com; powershell -ExecutionPolicy Bypass -File ops/github/apply-nex-main-protection.ps1 -Apply . Fazer login interativo apenas se Owner autorizar; nunca divulgar PAT.

O script lê repo e checks exatos das PRs #72/#73, cria ou atualiza o Ruleset gerenciado e confirma o GET completo. Somente após a verificação do Ruleset aplica o PATCH das configurações gerais squash-only e confirma novo GET; se qualquer condição falhar, para. Não modifica outros repositórios.

**Próximo arquivo:** docs/operations/NEX-CODEX-DESKTOP-START.md tem prompt completo para executar bootstrap GEF em Windows LOCAL depois de governança promovida, com evidence/CI e STOP conditions. Não instalar/aplicar às cegas.
