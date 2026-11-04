# Especificação funcional — Confirmação inicial no terminal

**Data:** 30/10/2026  
**Estado:** aprovada pelo usuário e implementada; 69 testes passaram sem operação visual.  
**Origem:** solicitação do usuário para corrigir a autorização inicial em `Automação.py`.  
**Documentos:** [plano técnico](plan.md) e [tarefas](tasks.md).

## Diagnóstico anterior à correção

Em `../../Automação.py`, linhas 392–397 na versão inspecionada, `main()` lê uma única resposta, remove espaços laterais com `.strip()` e compara o resultado diretamente com `"SIM"`. Não existe função dedicada de confirmação nem laço de repetição. Qualquer outra resposta produz `Seleção pendente; nenhuma saída comercial foi criada.` e retorno 2.

Isso explica a rejeição de `sim` e `Sim`, a ausência de distinção entre negativa e entrada inválida e o encerramento após a primeira tentativa. A pergunta atual também não apresenta a opção NÃO. A leitura está antes da criação da cópia e das chamadas visuais, posição que deve ser preservada. As confirmações posteriores do piloto e da continuação, atualmente nas linhas 436 e 447, são outros checkpoints e ficam fora desta correção.

Não foi reproduzido um problema de mensagens redundantes por execução: o código foi apenas inspecionado. A eliminação da redundância é um requisito do novo laço.

## Histórias e cenários de aceitação

### US1 — Autorizar com variação de caixa (P1)

Como operador, quero confirmar com SIM em qualquer combinação de caixa e com espaços laterais, para prosseguir sem rejeição desnecessária.

**Verificação independente:** fornecer respostas simuladas à confirmação, sem abrir Excel.

1. Dada a confirmação pendente, ao receber `sim`, `SIM`, `Sim`, `sIm` ou `  sim  `, registrar autorização positiva e sair da confirmação uma vez.
2. Após autorizar, continuar o fluxo existente uma vez, mantendo as validações de entradas, saída parcial, piloto, foco e integridade.

### US2 — Encerrar explicitamente (P1)

Como operador, quero recusar a autorização com NÃO ou NAO, para encerrar normalmente.

**Verificação independente:** simular a negativa e verificar a mensagem, o retorno de `main()` e a ausência de efeitos posteriores.

1. Ao receber `não`, `NÃO`, `Não`, `NAO`, `nao`, `Nao` ou uma dessas respostas com espaços laterais, exibir uma única vez `Automação encerrada pelo usuário.` e retornar 0 de `main()`.
2. Não criar diretório de execução, cópia de trabalho ou nova planilha final, nem abrir Excel ou enviar comandos PyAutoGUI. Saídas anteriores permanecem intactas, inclusive com `--retomar`.

### US3 — Corrigir entradas inválidas (P1)

Como operador, quero tentar novamente após erro de digitação, sem repetir explicações ou reiniciar o processamento.

**Verificação independente:** simular várias respostas e contar perguntas, mensagens e chamadas posteriores.

1. A pergunta inicial aparece exatamente uma vez por chamada da confirmação: **Confirma a seleção e autoriza abrir o Excel? Digite SIM para continuar ou NÃO para encerrar:**
2. Para cada entrada inválida, exibir apenas uma mensagem de validação: **Resposta inválida. A seleção permanece pendente. Digite SIM para continuar ou NÃO para encerrar a automação.**
3. Após a mensagem, ler outra resposta sem novo texto de pergunta. Repetir sem limite de tentativas até uma resposta válida.
4. Enquanto pendente, não criar saídas, abrir Excel, executar ações PyAutoGUI, repetir classificação ou reentrar em `main()`.

## Requisitos funcionais

- **RF01:** aceitar somente respostas que, após remover espaços laterais e ignorar caixa, sejam `sim`, `não` ou `nao`.
- **RF02:** considerar resposta vazia, somente espaços, palavras desconhecidas, `S`, `N`, `sim!` e `n a o` inválidas. Não remover espaços internos nem aceitar prefixos.
- **RF03:** uma resposta positiva produz autorização; uma negativa produz recusa. Entrada inválida mantém a decisão pendente e nunca retorna autorização.
- **RF04:** usar a pergunta e as mensagens especificadas acima, sem mensagem adicional de “seleção pendente” ao negar ou errar.
- **RF05:** não exigir mensagem positiva adicional: o retorno positivo confirma a autorização e permite a continuação normal.
- **RF06:** negativa é encerramento normal com retorno 0, e não falha técnica nem processamento comercial concluído. Os demais códigos de retorno e checkpoints continuam com o comportamento existente.
- **RF07:** alterar futuramente apenas a confirmação inicial em `Automação.py` e seus testes diretos em `tests/test_automacao.py`. Preservar classificação de duplicidades, bases, relatórios e automação visual.

## Matriz mínima de verificação futura

| Respostas na ordem | Resultado | Mensagens de entrada inválida |
|---|---|---:|
| `sim`, `SIM` ou `Sim` em casos separados | Autorizar uma vez | 0 |
| `não`, `NÃO`, `NAO` ou `nao` em casos separados | Encerrar normalmente | 0 |
| `  Sim  ` ou `  Não  ` em casos separados | Autorizar ou encerrar | 0 |
| vazia, `SIM` | Aguardar após a vazia; depois autorizar | 1 |
| somente espaços, `NÃO` | Aguardar; depois encerrar | 1 |
| `talvez`, vazia, `sim!`, `SIM` | Autorizar somente na quarta leitura | 3 |
| `x`, `S`, `n a o`, `NÃO` | Encerrar somente na quarta leitura | 3 |
| 100 entradas inválidas, `SIM` | Autorizar sem limite artificial | 100 |

## Critérios mensuráveis e limites

- Pergunta inicial: uma ocorrência por confirmação.
- Cada tentativa inválida: uma ocorrência exata da mensagem e nenhuma chamada visual ou criação de saída.
- Sequências válidas positivas: continuação uma vez; nenhum checkpoint posterior é autorizado implicitamente.
- Sequências negativas: mensagem exata uma vez, retorno 0 e zero saídas novas.
- Verificações futuras usam mocks e arquivos temporários; não operam a tela nem escrevem nos CSVs comerciais.
- EOF e Ctrl+C não são respostas de autorização. Não serão convertidos em SIM ou NÃO; conservar o tratamento de interrupções existente, sem expandir o escopo.

## Premissas

O terminal oferece entrada interativa. Esta mudança trata somente a confirmação anterior à criação da cópia e à abertura do Excel. Não há nova dependência, armazenamento de decisões ou alteração de dados comerciais. Os documentos gerais PRD/SPEC contêm descrições históricas de implementação pendente; o diagnóstico desta alteração usa o código atual como referência.
