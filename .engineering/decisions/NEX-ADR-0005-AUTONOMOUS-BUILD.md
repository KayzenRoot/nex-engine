# NEX-ADR-0005 | Construção autônoma contínua

**Status:** OWNER_APPROVED_ON_PROMOTION (2026-11-14)  
**Work Order:** NEX-GOV-AUTONOMY-WO-001, Issue #108  
**Autoridade:** diretiva expressa do Owner em 2026-11-14. Eficaz após PR de governança protegida, CI e merge.  
**Relação:** complementa NEX-ADR-0004 / NEX-D-014; não substitui nem relaxa nenhum gate.

## Decisão

O Owner autoriza o administrador a construir a NEX Engine de forma **contínua e autônoma**, sem pedir confirmação a cada incremento. O executor deve:

1. escolher o próximo incremento de maior valor entre os caminhos admitidos/enablers bounded;
2. executar ciclos longos (tipicamente 4–5 horas de trabalho útil quando disponível), encadeando WO, Context Lock, implementação, testes, Evidence Bundle, PR protegida, checks, squash e checkpoint;
3. prosseguir imediatamente para o próximo incremento após o checkpoint, sem aguardar nova pergunta;
4. manter `ADMIN_SOLO / NOT_INDEPENDENT`, WOs bounded, locks, fingerprints, evidência verificável, PR protegida, squash sem force-push e checkpoint pós-merge.

## Quando parar

Somente diante de:

- bloqueio técnico real (ferramenta/ambiente/hardware indisponível, captura inválida, dependência ausente);
- dependência ou parent não admitido que impeça o incremento;
- risco grave, perda de dados, segredo, dinheiro, signing, privilégio ou operação irreversível sem autorização específica;
- CI obrigatória vermelha/pendente, Context Lock STALE, divergência de base/HEAD ou defeito HIGH/CRITICAL;
- conflito de escrita com outro executor ou regra de plataforma que exija ação humana.

Nesses casos, registrar `BLOCKED_*` com evidência e parar — nunca contornar por bypass, supressão ou autoaprovação fictícia.

## Limites da autonomia

A autonomia **não**:

- admite automaticamente as issues PLANNING_ONLY ou parents M01–M12;
- relaxa checks, testes, segurança, revisão de risco, ruleset ou branch protection;
- autoriza force-push, reset destrutivo, limpeza destrutiva ou escrita concorrente;
- permite inventar medições, aprovações, licenças ou resultados;
- transforma autoauditoria em revisão independente.

## Consequências

O fluxo passa a ser pró-ativo e de longo fôlego, com o administrador escolhendo e documentando cada incremento. A qualidade é preservada pelos mesmos gates técnicos; a diferença é a ausência de pausas por confirmação ou por falta de revisor externo. O Owner pode revogar ou estreitar esta diretiva a qualquer momento; a revogação não reescreve evidências já promovidas.
