# Plano técnico — Confirmação inicial no terminal

**Data:** 30/10/2026  
**Estado:** aprovado, implementado e revisado independentemente; 69 testes passaram sem operação visual.  
**Especificação:** [spec.md](spec.md) · **Execução futura:** [tasks.md](tasks.md).

## Contexto e escopo

Projeto local em Python (ambiente registrado anteriormente: Python 3.14), Windows e Excel desktop. O código atual usa pandas, openpyxl, PyAutoGUI, pyperclip e biblioteca padrão. Esta alteração precisa apenas de `input`, `print` e métodos de string. Os testes existentes usam pytest e monkeypatch; nenhuma instalação adicional é necessária.

O armazenamento permanece nos CSVs e XLSX existentes. A confirmação não persiste estado nem produz arquivo. Não há meta temporal: a espera é controlada pelo operador, sem limite de tentativas.

## Arquivos envolvidos

- `../../Automação.py`: incluir a função local de confirmação e substituir somente o bloco inicial de decisão em `main()`.
- `../../tests/test_automacao.py`: incluir os casos da matriz de aceitação e a proteção de integração.
- Esta pasta: `spec.md`, `plan.md` e `tasks.md`, sem sobrescrever a documentação geral em `planejamento/projeto/`.

Não serão criados módulos, novos arquivos de teste, worktrees ou commits. Nenhuma operação visual é necessária para implementar ou verificar esta correção.

## Desenho proposto

1. Criar em `Automação.py` a função local `confirmar_abertura_excel`, sem argumentos, com retorno booleano. Ela apresenta a pergunta inicial uma única vez, lê e valida respostas até decidir. Não abre arquivos ou Excel, não executa PyAutoGUI e não chama `main()`.
2. Normalizar somente a resposta do terminal com `strip` e `casefold`. Comparar com `sim` para positivo e com `não`/`nao` para negativo, sem normalização dos dados comerciais.
3. Após cada resposta inválida, imprimir exatamente a mensagem definida e ler novamente sem prompt adicional. Usar laço iterativo, evitando recursão e limite de tentativas.
4. Retornar positivo para `main()` continuar no ponto já existente. Retornar negativo para `main()` imprimir a mensagem de encerramento e retornar 0 antes de preparar a cópia ou entrar em qualquer ramo de retomada.
5. A função de confirmação será a única responsável pela pergunta e pelas mensagens de resposta inválida; `main()` será responsável pela mensagem final de recusa. Essa divisão evita emissões duplicadas.

## Dependências e riscos de regressão

O único consumidor novo é `main()`, atualmente linhas 392–397. Leitura, validação e classificação continuam antes da pergunta; criação de saída, retomada e automação continuam depois dela. Não mover o laço para envolver `main()`, pois isso repetiria as etapas.

A negativa inicial passa de retorno 2 para retorno 0 por requisito de encerramento normal. Os retornos 2 dos checkpoints posteriores continuam válidos. Uma resposta positiva inicial não autoriza o lote piloto ou o restante.

Os testes atuais que fornecem SIM continuam compatíveis. Testes que forneçam entrada inválida constante precisam usar uma sequência finita terminada em SIM/NÃO para não aguardar indefinidamente. Não alterar expectativas de checkpoints posteriores por substituição global de mensagens ou retornos.

## Verificação planejada

Após aprovação, escrever primeiro testes parametrizados da função para caixa, acentos, espaços e matriz de tentativas. Registrar chamadas de `input` para conferir que somente a primeira possui a pergunta; capturar a saída para contar as mensagens exatas. Não depender do eco do terminal, que não é saída do programa.

Adicionar testes de integração de `main()` com I/O e GUI substituídos por mocks: negativa sem nova saída; inválidas sem efeitos posteriores enquanto pendentes; positiva acionando a preparação uma única vez; validação de entrada ainda capaz de bloquear a execução; checkpoint do piloto ainda exigindo decisão própria. Cobrir também negativa com `--retomar` sem publicação da saída final.

Executar testes focados e depois a suíte existente, sem iniciar a automação comercial. Revisar o diff para conferir a limitação à confirmação e às dependências diretas. Na elaboração documental não foram executados testes; após autorização, os ciclos de falha e sucesso e a suíte completa foram executados e registrados em `tasks.md`.

## Condição de conclusão

Matriz de aceitação aprovada, mensagens e contagens exatas, ausência de GUI/saída enquanto pendente ou recusado, continuação única e regressões existentes aprovadas. A implementação começa somente após autorização do usuário.
