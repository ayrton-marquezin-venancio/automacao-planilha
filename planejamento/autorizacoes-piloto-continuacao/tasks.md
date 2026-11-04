# Tarefas — Autorizações do piloto e da continuação

**Estado:** T01–T05 implementadas, verificadas com 153 testes aprovados e aprovadas em revisão independente. T06 foi autorizada, iniciada e encerrada por decisão do usuário após acionamento do fail-safe; aceite visual integral ainda não concluído.  
**Dependências:** [spec.md](spec.md) e [plan.md](plan.md). Os caminhos abaixo são relativos à raiz do projeto.

## US1 — Piloto

- [x] **T01:** Registrar o trecho atual de `confirmar_abertura_excel` e os hashes das fontes; em `tests/test_automacao.py`, criar os casos da função `confirmar_operacao` com a matriz da SPEC. Verificar falha antes de implementar, com GUI bloqueada.
- [x] **T02:** Em `Automação.py`, implementar a função comum e integrar somente a confirmação do piloto. Cobrir negativas sem abertura/inserção/publicação e preservação da cópia de trabalho, inclusive em retomada. Depende de T01.

## US2 — Continuação

- [x] **T03:** Em `tests/test_automacao.py`, cobrir a matriz no checkpoint de continuação, recusa depois do piloto, bytes da saída parcial preservados e zero publicação final. Integrar a segunda chamada à função comum em `Automação.py`, mantendo preenchimento e verificações existentes. Depende de T02.

## US3 — Foco e regressão

- [x] **T04:** Em `Automação.py`, capturar a janela de origem e restaurá-la antes da terceira pergunta, com verificação de identidade e orientação única para seleção manual do terminal integrado. Em `tests/test_automacao.py`, simular foco, falha de restauração e fluxo de retomada; conferir ordem das chamadas e ausência de inserção/publicação em falha. Depende de T03.
- [x] **T05:** Em `tests/test_automacao.py`, alinhar somente o espaço final da expectativa da primeira pergunta ao texto aprovado e executar sua regressão. Conferir que o trecho da função inicial e sua chamada não mudaram, executar testes focados e `python -m pytest tests/test_automacao.py -q`, revisar o diff e registrar resultados. Depende de T04.
- [ ] **T06:** Após autorização específica para controle de tela, verificar manualmente Excel → VS Code → terminal integrado → decisão → Excel, incluindo cancelamento após piloto e permanência da cópia parcial. Se o terminal não receber o foco correto, registrar a limitação e não aprovar esse critério. Depende de T05; não está autorizado nesta etapa.

Implementar em sequência, sem tarefas paralelas no mesmo arquivo. A correção só será declarada totalmente verificada depois dos critérios automatizados e do foco integrado efetivamente comprovados. Não executar `Automação.py` durante a elaboração destes documentos.

## Registro da execução

- Pre-flight: T01/T02 produzem `confirmar_operacao(pergunta) -> bool`, consumida por T03; T04 integra a janela capturada em `main()` antes da terceira leitura. A confirmação inicial é imutável; funções de dados, preenchimento e publicação não serão refatoradas.
- Ruling: manter este registro como ledger e não usar scripts Git/worktrees/commits da skill — o plano aprovado proíbe essas estruturas. Custo: o histórico desta alteração depende dos registros e verificações, sem commits.
- Ruling: aplicar os ciclos RED/GREEN do plano sem a subskill auxiliar `test-driven-development`, não encontrada anteriormente nos diretórios locais de skills. Custo: suas instruções adicionais não estão disponíveis; testes precedem cada mudança funcional.
- Baseline da primeira função: SHA-256 textual `625664ef23520216a83d69867d942faca41dc9e3a55c6b6de1038ae16424dd53`. Fontes: cadastro `9e2e6d1ffc2743c79bf0ec4accaa37ea70e9ab4c3863ffe573ba11c7baa807e1`; solicitações `16f0750759f07364bb33a207711cedb9599041f022d05829b1ced99b8652fd5e`.
- T01: 36 casos da função comum falharam por interface ausente (RED).
- T02: 12 casos de recusa no piloto, incluindo retomada, falharam com o código anterior. Após a implementação, `python -m pytest tests/test_automacao.py -q -k 'operacao_interpreta or piloto_recusa'`: 48 passaram. Testes em diretórios temporários, com GUI bloqueada.
- T03: 26 casos de integração da continuação/autorizações do piloto falharam antes da alteração do checkpoint 3. Após a integração, 74 casos focados passaram; cancelamentos mantêm os bytes da cópia parcial e não publicam nem substituem arquivos finais anteriores.
- T04: 7 casos de restauração/ordem/falha de foco falharam antes da integração; após captura da janela e restauração por identificador, 83 casos focados passaram (incluindo interrupções de entrada). A API é simulada, inclusive nos testes antigos: nenhuma janela real recebe `activate()`.
- Ruling: validar também o título de host VS Code junto ao identificador capturado — impede reativar outro aplicativo capturado por engano, sem procurar janela por título. Custo: um VS Code com título totalmente personalizado sem “Visual Studio Code” será bloqueado com diagnóstico antes da continuação.
- T05: a suíte revelou 38 expectativas antigas incompatíveis (espaço final já presente na pergunta inicial, textos e retornos antigos dos checkpoints); alinhadas às regras aprovadas sem alterar a primeira função. `python -m pytest tests/test_automacao.py -q`: 153 passaram em 7,62 s, com todos os acessos de foco simulados.
- Comparação com a captura anterior: das 18 funções originais, somente `main()` foi modificada; `confirmar_abertura_excel` e as outras 16 funções foram preservadas textualmente. Novas funções locais: `confirmar_operacao` e `_restaurar_foco_terminal`. Hashes dos CSVs comerciais continuam iguais ao baseline.
- T06: pendente; nenhuma operação real de mouse/teclado, abertura de Excel ou ensaio visual foi executado. Reativação da janela não comprova foco no painel interno: o teste manual continua necessário.
- Revisão independente `review_autorizacoes_piloto_continuacao`: aprovada, sem achados críticos, importantes ou menores; confirmou estaticamente a AST válida e o hash da primeira função. Nenhuma correção adicional foi solicitada.
- Final: Ruling: foco no painel integrado permanece sem aceite visual — T06 exige autorização específica ainda não recebida. Custo: a interface real ainda pode exigir seleção manual do terminal.
- Final: Ruling: manter o bloqueio de títulos personalizados/outros hosts — mantém o escopo VS Code e a validação de identidade planejada. Custo: esses ambientes precisam de adaptação futura antes da continuação.
- Final: Ruling: não acrescentar checkpoints a lote sem novos, retomada completa ou piloto que completa o lote — são fluxos existentes preservados. Custo: esses caminhos continuam concluindo sem uma terceira pergunta desnecessária.
- Final: Ruling: preservar seleção do Excel, preenchimento, salvamento e validação comercial — comparação textual confirmou funções intactas e a suíte passou. Custo: não houve nova auditoria visual/comercial completa dessas rotinas.
- Final: Ruling: conservar Ctrl+C/EOF — interrupções não viram autorização, mantendo o comportamento anterior. Custo: Ctrl+C pode propagar KeyboardInterrupt, e EOF continua como erro geral de entrada.
- Não há achados menores adiados. Documentação atualizada; sem commits, push, worktrees ou alterações de configuração.

## Ensaio T06 — 30/10/2026 (horário do usuário)

- Autorização recebida: somente 3 equipamentos em nova cópia, com cancelamento da continuação, sem inserir os 197 restantes.
- O arquivo atual foi iniciado pelo botão Python no terminal integrado do VS Code. A primeira confirmação aceitou `sim`; no piloto, `talvez` exibiu uma única mensagem de inválida sem repetir a pergunta; `Sim` autorizou o piloto.
- A captura/entrada do provedor de UI falhou (timeout de captura e geometria indisponível). Foi utilizada a biblioteca PyAutoGUI do projeto, expressamente autorizada para o ensaio, para captura e respostas aos prompts.
- A automação foi interrompida por `FailSafeException`, cuja mensagem informa ponteiro em um canto da tela. Nenhuma tentativa de desativar ou contornar o fail-safe foi feita. O usuário confirmou que a interrupção foi intencional e pediu para encerrar o ensaio. Não foram enviados novos comandos à interface após a interrupção.
- Auditoria somente leitura: `saidas/execucao_20261031T011342918000Z/equipamentos_atualizados_20261031T011342918000Z.xlsx` contém 345 registros de dados: 342 originais e 3 novos (`EQP0524`, `EQP0404`, `EQP0507`). `verificar_xlsx` aprovou os cinco atributos e a ordem contra as fontes. `equipamentos_atualizados.xlsx` não foi publicado nessa execução. Hashes dos CSVs iguais ao baseline; `pyautogui.FAILSAFE` continua `True`.
- A terceira confirmação e o foco interno no terminal não foram comprovados no ensaio interrompido. T06 permanece desmarcada, sem desfazer as aprovações automatizadas de T01–T05.
- Ruling: respeitar a decisão explícita de encerrar o ensaio — autorização anterior não é usada para prosseguir após a interrupção intencional. Custo: o aceite visual da terceira confirmação e do foco integrado permanece incompleto.
