# Plano técnico — Autorizações do piloto e da continuação

**Estado:** aprovado e implementado; T01–T05 verificadas; T06 executada parcialmente e encerrada pelo usuário após fail-safe. Aceite visual integral pendente.  
**Contrato:** [spec.md](spec.md) · **Tarefas:** [tasks.md](tasks.md).

## Contexto e alteração mínima

Python 3.14, Windows, execução no terminal integrado do VS Code confirmada pelo usuário. Manter pandas, openpyxl, PyAutoGUI e pyperclip existentes; nenhuma dependência nova. Alterar futuramente apenas `../../Automação.py` e `../../tests/test_automacao.py`, além do registro desta documentação.

1. Acrescentar no mesmo script uma função `confirmar_operacao(pergunta: str) -> bool`, usada exclusivamente pelos checkpoints 2 e 3. Reproduzir as regras `.strip().casefold()` e o laço da função aprovada, com a nova mensagem de inválida. Não parametrizar, mover ou alterar a primeira confirmação: a restrição de preservá-la prevalece sobre extrair um mecanismo único para as três.
2. Substituir apenas os dois blocos de `input`/comparação em `main()` por chamadas à função comum. No retorno negativo, informar encerramento e caminho da cópia preservada como parcial, e retornar 0 antes dos comandos posteriores. A autorização positiva mantém os checkpoints e a sequência atuais.
3. Capturar a janela de origem imediatamente após o primeiro SIM, antes da interação gráfica, sem tocar na função inicial. Usar a API de janelas já disponível por PyAutoGUI. Antes da terceira pergunta, ativar essa mesma janela e conferir sua identidade, sem escolher janela por título genérico ou ordem da lista. Falha de identificação/restauração deve interromper de forma explícita.
4. Para o terminal integrado, limitar o retorno automático à janela identificada. Informar uma única vez que o operador deve selecionar o terminal do script antes de responder. A API atual de janelas não comprova o foco no painel interno. Não acrescentar atalhos para alternar painéis, comandos digitados, configurações do VS Code ou novos terminais. Validar o foco interno manualmente em ensaio autorizado separado.
5. Manter a saída parcial já salva e o Excel como estiverem no cancelamento; nenhuma limpeza ou publicação adicional. Não alterar funções de salvamento, validação, retomada, classificação ou inserção. As chamadas de reativação do Excel após autorizar continuam existentes.

## Verificação futura

- Testes parametrizados da função para toda a matriz da SPEC, contagem exata da pergunta e mensagem e sequência ilimitada de tentativas, com `input` simulado.
- Integração de `main()` com GUI simulada: recusa no piloto não chama abertura/inserção; recusa após piloto não chama inserção restante nem `shutil.copyfile`; cópia parcial permanece igual; aprovações não repetem etapas.
- Ordem de foco: captura de janela antes do piloto, restauração antes da leitura da terceira decisão e reativação de Excel somente após SIM. Falha de foco não autoriza nem publica. A execução retomada também precisa de captura, ainda que pule o piloto.
- Regressão da primeira confirmação: comparar o trecho textual ao baseline e verificar caixa, negativa e inválidas com seus textos próprios. **Divergência observada sem executar testes:** a pergunta salva termina com `: `, mas `PERGUNTA_CONFIRMACAO` em `tests/test_automacao.py` termina com `:`. Alinhar somente essa expectativa ao texto atual aprovado, sem modificar a função ou sua mensagem.
- Executar testes focados e suíte existente somente após autorização da implementação; todos sem GUI real. Revisar diff e integridade das fontes. Revisão automática não comprova foco dentro do terminal.

## Limites e aceite

Não criar módulos, novos arquivos de teste, commits ou alterações de configuração. O ensaio manual posterior deverá verificar o terminal que executa o script, com foco inicialmente no Excel e no editor, e comprovar que respostas não são digitadas na planilha ou no código. A funcionalidade de interpretação pode ser verificada sem tela; o aceite do foco integrado permanece pendente até esse ensaio autorizado.

Referência de contexto: o VS Code gerencia terminais e grupos separadamente dentro da mesma janela; consultar a documentação de [terminal integrado](https://code.visualstudio.com/docs/terminal/basics) para a verificação operacional. A captura/reativação de janela e o checkpoint manual descritos acima são decisões deste plano.
