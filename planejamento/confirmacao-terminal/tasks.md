# Tarefas — Confirmação inicial no terminal

**Documentos:** [spec.md](spec.md) e [plan.md](plan.md).  
**Estado:** T001–T009 concluídas; 69 testes passaram; revisão independente aprovada, sem achados no escopo da alteração.

Os caminhos abaixo são relativos à raiz `7 - Automação de Cadastro de Equipamentos/`. Executar em ordem após aprovação. As histórias compartilham o mesmo laço e os mesmos arquivos; não implementar em paralelo.

## US1 — Autorizar com variação de caixa

- [x] **T001:** Em `tests/test_automacao.py`, escrever casos parametrizados para a futura função `confirmar_abertura_excel`: `sim`, `SIM`, `Sim`, `sIm` e espaços laterais; conferir retorno positivo e pergunta exata uma vez. Verificar a falha antes da implementação, sem GUI.
- [x] **T002:** Em `Automação.py`, criar a função local com normalização `strip`/`casefold`, mantendo toda ação de arquivo e GUI fora dela. Depende de T001; o laço completo é concluído nas histórias seguintes antes da integração.

## US2 — Recusar com encerramento normal

- [x] **T003:** Em `tests/test_automacao.py`, incluir casos para `não`, `NÃO`, `Não`, `NAO`, `nao`, `Nao` e espaços laterais. Em `Automação.py`, implementar o retorno negativo da função. Depende de T002.

## US3 — Manter entradas inválidas pendentes

- [x] **T004:** Em `tests/test_automacao.py`, incluir vazia, espaços, desconhecida, prefixos e espaços internos; sequências de três inválidas seguidas de SIM/NÃO e de 100 inválidas seguidas de SIM. Conferir uma pergunta, uma mensagem exata por tentativa e ausência de mensagens extras. Depende de T003.
- [x] **T005:** Em `Automação.py`, concluir o laço iterativo de confirmação: após erro, mensagem exata uma vez e nova leitura sem pergunta. Não chamar `main()` nem reiniciar classificação. Executar os testes focados com mocks. Depende de T004.

## Integração e revisão das três histórias

- [x] **T006:** Em `tests/test_automacao.py`, preparar verificações de `main()` para negativa direta e após inválidas: retorno 0, mensagem de encerramento uma vez e nenhuma chamada de preparação, publicação, abertura ou inserção. Incluir negativa com saída parcial existente. Depende de T005.
- [x] **T007:** Em `Automação.py`, substituir somente o bloco inicial de confirmação de `main()` pelo uso da função; na recusa, imprimir `Automação encerrada pelo usuário.` e retornar 0. Preservar os demais checkpoints e códigos de retorno. Depende de T006.
- [x] **T008:** Em `tests/test_automacao.py`, confirmar que inválidas não produzem efeitos enquanto pendentes, positiva continua uma vez, entradas inválidas de negócio continuam bloqueando a execução e a autorização inicial não dispensa a do piloto. Executar os testes focados e `python -m pytest tests/test_automacao.py -q`, com GUI simulada. Depende de T007.
- [x] **T009:** Revisar as alterações somente em `Automação.py` e `tests/test_automacao.py`, conferir mensagens e todos os cenários de `spec.md`, registrar resultados e limitações e submeter o resultado ao usuário. Depende de T008. Não executar a automação comercial.

## Critério de entrega

T001–T009 aprovadas; nenhuma modificação das bases, da identificação de duplicados ou da rotina de inserção. Resultados de testes só serão registrados após execução efetiva. Nenhum controle de tela é necessário para essas tarefas.

## Registro de execução

- Ruling: usar este registro como ledger e dispensar scripts de workspace/commits da skill — o plano aprovado proíbe worktrees, commits e arquivos auxiliares desnecessários; a execução permanece nos arquivos autorizados. Custo: não há histórico Git desta alteração; as evidências ficam neste registro e nos testes.
- Ruling: a subskill `test-driven-development` não foi encontrada nos diretórios de skills `.agents` e `.codex`; aplicar os ciclos de falha e sucesso explicitamente prescritos no plano. Custo: não foi possível consultar instruções adicionais dessa subskill.
- Pre-flight: T001–T005 produzem `confirmar_abertura_excel() -> bool`; T006–T008 integram esse contrato a `main()`. Mensagens de erro pertencem à função e mensagem de recusa pertence a `main()`: sem conflito de interfaces.
- T001–T002: 5 casos positivos falharam por função ausente e passaram após implementação.
- T003: 8 casos negativos falharam por retorno não booleano e passaram após implementação; 13 casos de confirmação passaram.
- T004–T005: 17 casos de entradas inválidas falharam antes do laço e passaram após ele. Comando `python -m pytest tests/test_automacao.py -q -k confirmacao`: 30 passaram, 28 desmarcados; nenhuma interação visual.
- T006: 6 casos de recusa em execução nova/retomada falharam com o retorno 2 do código anterior.
- T007–T008: integração positiva e recusa falharam antes da substituição do bloco; após a integração, `python -m pytest tests/test_automacao.py -q` passou com 69 testes (28 preexistentes + 41 novos casos parametrizados), em 4,35 s. Todos os dados de teste estão em memória ou diretórios temporários.
- Conferência de escopo: comparação com o código capturado antes da edição confirmou somente a inclusão de `confirmar_abertura_excel()` e a substituição do bloco inicial de `main()`. Demais funções, classificação e checkpoints não foram alterados.
- Integridade: hashes SHA-256 dos CSVs comerciais iguais antes/depois: `equipamentos_cadastrados.csv` = `9e2e6d1ffc2743c79bf0ec4accaa37ea70e9ab4c3863ffe573ba11c7baa807e1`; `novos_equipamentos.csv` = `16f0750759f07364bb33a207711cedb9599041f022d05829b1ced99b8652fd5e`.
- T009: revisão independente somente leitura pelo agente `review_confirmacao_terminal`: aprovada, sem achados críticos, importantes ou menores. A revisão conferiu os requisitos, o laço, os efeitos posteriores e a cobertura; não executou automação ou testes adicionais.
- Final: Ruling: operação real de foco, colagem e salvamento não foi revalidada — o usuário proibiu abertura do Excel e execução comercial; a confirmação é verificada por testes com bloqueio de GUI. Custo: esta entrega não comprova novamente a integração visual real.
- Final: Ruling: classificação, integridade comercial e publicação não receberam auditoria integral nova — permanecem fora da alteração, com funções preservadas e suíte preexistente aprovada. Custo: problemas preexistentes fora da confirmação podem permanecer.
- Final: Ruling: conservar a experiência existente de EOF/Ctrl+C — especificação exclui seu redesenho; testes conferem que interrupções não viram autorização. Custo: nenhuma melhoria de mensagem nessas interrupções.
- Final: Ruling: não adicionar normalização Unicode extra ou abreviações — o contrato aceita somente as respostas normalizadas por strip/casefold. Custo: formas Unicode não equivalentes por casefold e abreviações continuam inválidas.
- Final: Ruling: comparação histórica do restante do código foi feita pelo executor contra o conteúdo capturado antes da edição — confirmou escopo exato; o revisor não possuía baseline Git independente. Custo: a evidência histórica depende dessa captura, sem diff Git.
- Não houve achados menores adiados nem correções adicionais após a revisão. O Excel, o mouse e o teclado não foram operados; nenhum relatório comercial novo foi gerado.
