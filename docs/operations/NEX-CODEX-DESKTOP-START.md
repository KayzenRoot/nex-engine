# PROMPT ÚNICO | CODEX DESKTOP LOCAL | NEX GEF + HARDENING DO GITHUB

**Repo:** https://github.com/KayzenRoot/nex-engine
**Objetivo:** finalizar GEF Bootstrap 1.1.2 e preparar início seguro do desenvolvimento Godot após checks.
**Executar:** Codex Desktop Windows LOCAL, Git, Node.js 22, npm, gh CLI, Docker Desktop quando necessário; NÃO usar Codex Cloud nem serviços pagos.
**Owner directive:** Como ChatGPT não consegue baixar o npm neste ambiente, você está autorizado a atuar como fallback LOCAL para o bootstrap, sempre respeitando os gates. Não codar engine/módulos M00–M12 até bootstrap aprovado.

## 0. Conferência real e governança
1. Inspecione gh auth status, git status, remotes, main HEAD exato, permissões e worktrees. Se gh estiver desconectado, solicitar login interativo no Windows ao Owner, sem expor PAT/token. Não presumir que este chat autoriza burlar gate.
2. Leia AGENTS.md, todos os documentos .engineering relevantes, CHECKPOINT.json/md, NEX-ADR-0001 e NEX-ADR-0002, issue GEF #1, PRs #2 e #72, Orchestrator #4, Contracts #19, Bug Hunter #20.
3. O Source Pack PR #2 foi integrado em main como a238f610f0c1bfc2e45b33b38c45dec2ab39ca3c. A PR #72 promove governança e ADR #0002. Se ainda estiver aberta com CodeRabbit pendente, NÃO faça merge nem afirme que as autoridades já estão promovidas. Corrija findings por ChatGPT quando possível; aceite merge apenas após checks exatos, threads resolvidas e auditoria Owner/Steward. Sem bypass. Registre o SHA final da main.
4. Rebind o Context Lock de execução ao main exato, fingerprints e Source Pack promovido e registre admission específica de NEX-GEF-WO-001 #1 ANTES do apply. Fonte conflitante ou PR #72 não promovida = BLOCKED para mutação.

## 1. Configurar main segura no GitHub
1. A partir da branch de preparação ops/nex-main-ruleset-and-codex-bootstrap-001, leia ops/github/README.md, ops/github/nex-main-ruleset.json e ops/github/apply-nex-main-protection.ps1.
2. Rode em PowerShell **primeiro sem -Apply**:
   powershell -ExecutionPolicy Bypass -File ops/github/apply-nex-main-protection.ps1
3. Após PR #72 efetivamente integrada, CodeRabbit SUCCESS e os checks Socket SUCCESS no SHA revisado, usar gh CLI autenticado com permissão admin e rodar:
   powershell -ExecutionPolicy Bypass -File ops/github/apply-nex-main-protection.ps1 -Apply
4. Confirmar GET de repo e Rulesets: ACTIVE, target main, pull_request obrigatório, squash-only, linear history, non_fast_forward, anti-delete, threads resolvidas, strict up-to-date e contexts exatos CodeRabbit, Socket Security: Pull Request Alerts e Socket Security: Project Report. Não exigir jobs GEF CI que ainda não existam. Aprovação humana formal 0 porque o repo tem apenas Owner conhecido; isso não dispensa CodeRabbit e owner audit. Quando houver segundo aprovador real, propor 1 required review.
5. Se GitHub API devolver FORBIDDEN ou gh auth falhar, não fingir mudança; reportar ADMIN_BLOCKED e comando/Settings necessários. Não habilitar bypass, não mexer em outros repositórios. Não forçar merge.

## 2. Instalar GEF de verdade no Windows, com CI reproduzível
1. Fonte verificada: release GEF v1.1.2 https://github.com/KayzenRoot/gef-bootstrap/releases/tag/v1.1.2 ; tag aponta commit af1fe9371a3883cbd8a4aafcbb405ddcd4c2ca82; pacote @gef-bootstrap/cli@1.1.2 no npm. Alguns docs na tag usam texto histórico de pré-publicação, não confundir com release. Verificar registry dist.integrity/proveniência local antes de usar.
2. Crie somente após admissão um worktree+branch próprios da WO #1, a partir de main promovida e clean. Confirme Node.js 22, npm, Git e docker info (se Docker falhar, registrar bloqueio específico sem impedir tarefas que não dependem dele).
3. Se necessário crie package.json mínimo, instale a versão pinada como devDependency: npm install --save-dev --save-exact @gef-bootstrap/cli@1.1.2; gere package-lock real, e valide npm ci. Não baixar via serviço extra pago, não inventar lockfile, não depender de instalação global.
4. Verifique binário local gef --version (exatamente 1.1.2), --help, doctor --target . --json, status --target . --json e init --target . --json **somente preview, sem --apply**. Registre exit codes e arquivos afetados, risco de colisão com Source Pack, permissões/backup/recovery.
5. Executar init --target . --apply --json somente se aprovado pelo plano, checkpoint/Context Lock/admission corretos e efeitos não destrutivos. Qualquer conflito, symlink inesperado ou dados privados = BLOCKED, nunca --force ou excluir .gef-private.
6. Acrescentar GitHub Actions smoke Linux e Windows com Node 22, npm ci, comandos read-only. Validar no SHA exato da PR, CI com nomes de jobs únicos, sem segredos. Não usar CI Linux/Docker como benchmark GPU Windows.
7. Gerar Evidence Bundle com base/head SHAs, comandos/saídas reais e links, npm dist.integrity verificado, versões, preview/apply, rollback e Checkpoint Delta PROPOSTO; abrir PR própria para GEF e não fazer merge/self-approval sem CodeRabbit/Socket/CI/Owner.

## 3. Loop de reviews (regra do Owner)
Depois que Codex abre PR e para de escrever nos paths, ChatGPT corrige aqui primeiro qualquer finding de CodeRabbit/CI/Bug Hunter dentro do escopo e testável no GitHub, sob lock exclusivo. Mandar novamente para Codex APENAS tarefas impossíveis ou não verificáveis aqui (Windows/Docker/Godot GUI/GPU), com Correction Delta mínimo. Todos os fixes exigem nova verificação do HEAD e CodeRabbit/CI. Não usar Branch compartilhada concorrente.

## 4. Início do desenvolvimento
Quando GEF realmente instalado, inicializado, CI verde, documentação promovida, checkpoint auditado e Owner admission M00, preparar Godot native Windows baseline/build/CI. Só depois disso rodar Codex multiagente local, worktrees individuais, Integration Steward, Bug Hunter e 1 tarefa GPU pesada por vez. M01 definirá métricas FPS p95/p99, 1% low e input delay; nunca afirmar ganho sem benchmark.

## SAÍDA FINAL
Em português com links e SHAs: PR #72/merge, ruleset ID/enforcement readback, merge settings, Node/npm/Docker, pacote GEF versão/proveniência, preview/apply e possíveis conflitos, PR/CI exato HEAD, gates pendentes e próxima ação. Estados VERIFICADO/PENDENTE/BLOQUEADO/INCONCLUSIVO. STOP se PR pendente, estado STALE, CI falho ou risco HIGH/CRITICAL. Não consumir tempo do Codex corrigindo problemas que ChatGPT pode corrigir aqui.
