# NEX-ADR-0024 · Admissão do reference build Windows x86_64

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-17
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `4f822fc9dbe7b2b54d12a470913b3c33ddb8f88b`
**Issue:** #300

## Contexto

O Owner autorizou compilar e testar a NEX Engine após a conclusão dos módulos base. O `nex_bench` já contém o visual lab unificado com as cenas de referência, toolbar F1–F4, diagnóstico F9, observação F10 e GPU profiler F11. Porém, `scenes/base/project.godot` e `stress/project.godot` fazem o Godot tratar esses diretórios como projetos separados, e o export do projeto pai omitia as cenas base e o density ladder. Também não havia preset de export, ícone de build, script de staging, evidência de artefato ou teste GUI do executável.

## Decisão

Admitir, de forma **bounded e local**, um reference build Windows x86_64 do visual lab unificado:

- **Preset Windows Desktop** com `embed_pck=true`, arquitetura x86_64 e ícone ICO do M12.
- **Staging determinístico:** copiar `nex_bench` para `build/stage`, remover os `project.godot` aninhados e os entry points standalone (`viewer.tscn`, `viewer.gd`, `stress/main.tscn`) que não fazem parte do lab unificado, preservando as três cenas base e o density ladder.
- **Build oficial:** Godot 4.7.2-stable (`ed1daf0bf...`) e export templates oficiais Windows x86_64, com SHA-256 registrado.
- **Verificação:** smoke staged, export release, execução headless do `.exe` e teste GUI F1–F4/F9 com cinco capturas de janela.
- **Evidência:** `reference-build.v1.json`, `REFERENCE-BUILD.md`, capturas e gate.
- **Reprodutibilidade:** `scripts/build_reference_export.py --build --gui`; `--check` valida preset, ícone, evidência, hashes e ausência do `.exe` no Git.
- **CI:** `--check` no Fast Lane; o build real permanece local porque depende de templates e GPU/janela.

## Escopo de arquivos admitido

- `nex_bench/export_presets.cfg`, `nex_bench/icon.ico`.
- `scripts/build_reference_export.py`, `scripts/capture-reference-gui.ps1`.
- `docs/benchmarks/build/**` (evidência, relatório, capturas e gate).
- `tests/ci/test_reference_build.py`.
- `.github/workflows/nex-ci-fastlane.yml`, `.gitignore`.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #300.

## Exclusões explícitas

- Nenhum installer, code signing, auto-update, loja, publicação ou distribuição.
- Nenhuma alteração no engine Godot, renderer core, shader, cena de produção, gameplay, rede ou hub além do necessário para o export.
- Nenhum asset de terceiros; o ícone é o ICO original do M12.
- Nenhum claim de FPS, GPU p95, VRAM, qualidade visual, paridade com PoE2 ou aprovação de marca.
- Licença de distribuição e trademark permanecem `DISTRIBUTION_TRADEMARK_PENDING`.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. `build_reference_export.py --build --gui` produz o `.exe`, smoke staged PASS, headless PASS e 5 capturas GUI.
3. `build_reference_export.py --check` PASS no CI.
4. Artefato não versionado; `build/` ignorado.
5. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.
6. O fechamento de #300 só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- A NEX Engine passa a ter um executável Windows reproduzível do visual lab de referência.
- O build é uma ferramenta de validação local, não um release de produto.
- Uma futura distribuição exige decisão de licença/trademark, installer, assinatura e uma Work Order própria.
