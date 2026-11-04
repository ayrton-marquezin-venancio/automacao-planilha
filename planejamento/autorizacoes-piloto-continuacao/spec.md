# Especificação — Autorizações do piloto e da continuação

**Estado:** aprovada e implementada; 153 testes aprovados. Ensaio visual parcial encerrado pelo usuário após fail-safe; aceite do foco integrado pendente.  
**Origem:** requisitos do usuário e inspeção do código salvo em 30/10/2026.  
**Documentos:** [plano](plan.md) · [tarefas](tasks.md).

## Diagnóstico

Em `../../Automação.py`, `main()` compara `.strip()` diretamente com `"SIM"` na linha 603 (piloto) e nas linhas 616–620 (continuação). Qualquer outro texto retorna 2, sem distinguir negativa de erro de digitação e sem permitir nova tentativa.

`confirmar_abertura_excel()`, linhas 497–519, já interpreta respostas com `.strip().casefold()` e laço. Ela possui pergunta e mensagem próprias fixas: chamá-la nas outras etapas exibiria a pergunta errada. A função e a chamada inicial aprovadas devem ser preservadas integralmente.

Após o piloto, `_ativar_excel()` e `inserir_no_excel()` deixam o Excel ativo. O código pede a terceira resposta por `input()` sem restaurar o foco. Não há evidência de retorno correto ao terminal. O usuário confirmou que executa no terminal integrado do VS Code; focar somente a janela do VS Code não comprova foco no painel correto.

## Histórias e requisitos

### US1 — Autorizar ou recusar o piloto (P1)

O operador decide se o lote piloto pode começar. A pergunta será:

`Autoriza o lote piloto na tela? Digite SIM para continuar ou NÃO para encerrar:`

SIM autoriza exatamente o lote previsto, uma vez. NÃO encerra normalmente com retorno 0, sem abrir/ativar Excel para o lote, inserir registros ou publicar resultado final. A cópia de trabalho já criada permanece salva; em uma retomada, preservar também os registros existentes.

### US2 — Autorizar ou recusar a continuação (P1)

Após a verificação do piloto, o operador decide se libera os equipamentos restantes. A pergunta será:

`Autoriza continuar o preenchimento? Digite SIM para continuar ou NÃO para encerrar:`

SIM mantém as verificações existentes e insere apenas os pendentes, uma vez. NÃO encerra normalmente com retorno 0, sem preencher o restante e sem executar a publicação final.

**Política proposta de cancelamento:** preservar a cópia de trabalho salva e verificada, informar seu caminho e identificá-la como execução interrompida/saída parcial. Não criar `equipamentos_atualizados.xlsx` como resultado desta execução cancelada. Não excluir, mover, fechar o Excel nem salvar/descartar automaticamente eventuais edições manuais não confirmadas. Uma retomada continua sujeita à verificação integral já existente. Arquivos finais preexistentes não serão apagados.

### US3 — Corrigir respostas e responder no terminal correto (P1)

Para ambas as perguntas:

- Remover espaços laterais e ignorar caixa. Aceitar `sim` como positivo e `não`/`nao` como negativo.
- Considerar vazia, somente espaços e quaisquer outros textos inválidos, inclusive abreviações e palavras com pontuação.
- Exibir a pergunta inicial uma única vez por checkpoint. A cada inválida, imprimir exatamente uma vez: `Resposta inválida. A confirmação permanece pendente. Digite SIM para continuar ou NÃO para encerrar a automação.`
- Ler novamente sem repetir a pergunta nem acrescentar outra orientação de erro. Não limitar tentativas nem reiniciar classificação, criação de cópia ou inserção.
- Antes da terceira pergunta, reativar a janela de origem capturada no VS Code. Se não puder identificá-la/restaurá-la, interromper com diagnóstico sem inserir mais dados ou publicar saída final.
- A restauração da janela não será tratada como prova de foco no terminal integrado: orientar uma única vez o operador a selecionar o terminal que executa o script antes de responder e verificar esse fluxo manualmente no aceite visual. Não enviar SIM/NÃO ou comandos para obter foco, não usar Alt+Tab arbitrário nem criar outro terminal.

## Matriz de aceitação — aplicar a US1 e US2

| Resposta ou sequência | Resultado | Mensagens de inválida |
|---|---|---:|
| `SIM`, `sim`, `Sim`, `sIm` em casos separados | Autorizar uma vez | 0 |
| `NÃO`, `não`, `NAO`, `nao`, `Não` em casos separados | Encerrar com segurança | 0 |
| `  Sim  ` / `  Não  ` | Autorizar / encerrar | 0 |
| `talvez`, `123`, vazia, espaços em casos separados | Permanecer pendente | 1 por entrada |
| `talvez` → `sim` | Aguardar e depois autorizar | 1 |
| `ok` → `não` | Aguardar e depois encerrar | 1 |
| `erro` → `123` → `SIM` | Autorizar somente na terceira leitura | 2 |
| 100 inválidas → `NÃO` | Encerrar somente na leitura válida | 100 |

Nos casos pendentes, nenhuma nova inserção ou publicação pode ocorrer. Na US2, as linhas do piloto já salvas continuam disponíveis. Cenários sem resposta válida serão verificados com entrada simulada que observa o estado pendente, sem teste que aguarde indefinidamente.

## Preservação e critérios de conclusão

A primeira confirmação deve conservar código, textos, respostas e efeitos. Seu SHA-256 textual atual, obtido com `ast.get_source_segment` e codificação UTF-8, é `625664ef23520216a83d69867d942faca41dc9e3a55c6b6de1038ae16424dd53`.

Critérios: matriz aprovada nos dois checkpoints; pergunta única; uma mensagem por inválida; recusa sem publicação; nenhuma reinserção do piloto; primeira confirmação idêntica; processamento comercial e comandos de preenchimento preservados. EOF/Ctrl+C nunca viram autorização; conservar seu tratamento existente.

Os testes usam mocks e saídas temporárias. Após aprovação, foram executados 153 testes, todos aprovados, sem operar a tela. Em ensaio visual separado e autorizado, foram validados 3 equipamentos salvos e a tentativa inválida/positiva do piloto. O fail-safe interrompeu a execução e o usuário confirmou encerramento intencional. A terceira confirmação e o foco integrado permanecem sem aceite visual; detalhes em `tasks.md`.
