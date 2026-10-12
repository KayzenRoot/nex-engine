# Falha inicial e correção

Na primeira execução local de `tests/ci`, o conjunto coletou 72 testes e falhou em quatro casos de verificação de fixtures visuais:

- `test_local_validator_matches_ci` (o verificador local apontou `corridor_static`);
- `test_three_scene_hashes_match_fixtures_and_index` para `corridor_static`, `arena_combat` e `dense_city`.

Causa confirmada: o checkout Windows materializou os arquivos `.tscn` com CRLF por causa da configuração local de conversão de finais de linha, enquanto os SHA-256 das fixtures representam os bytes LF canônicos dos blobs Git. Não houve divergência de conteúdo das cenas. Exemplos observados: `corridor_static` calculado como `afc80a959a63373096b77e6a0680f7822af698d0e38e4039923ee45616f1fd13` com CRLF e esperado `9fada790391ce170e34115742f61ec1aa4b98d251b21a73dec675166fc20d773` com LF; os demais dois casos tinham a mesma classe de diferença.

Correção limitada ao verificador e ao teste: normalizar `\r\n` para `\n` antes do hash. Nenhuma configuração Git global/local foi modificada e nenhum arquivo de cena ou core foi alterado.

Após a correção: CI local `72/72 PASS`, contratos `12/12 PASS`, telemetria `31/31 PASS` (115/115 no total). Logs anteriores brutos permanecem apenas no computador local; a cópia bruta contém caminhos pessoais e não foi publicada.
