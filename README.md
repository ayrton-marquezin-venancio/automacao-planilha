# Cadastro de Equipamentos — Automação assistida com Python e Excel

Automação local de cadastro patrimonial que compara solicitações com uma base existente, seleciona equipamentos inéditos e preenche uma cópia de trabalho no Excel. O fluxo combina **tratamento de dados com Pandas**, **automação visual com PyAutoGUI** e **validação do arquivo salvo com Openpyxl**.

O projeto foi desenvolvido para exercitar uma rotina empresarial completa: receber dados, evitar cadastros repetidos, solicitar autorização, executar o preenchimento e conferir o resultado. A operação é assistida pelo analista; não é uma rotina autônoma em segundo plano.

## Problema e proposta

Copiar solicitações diretamente para um cadastro pode repetir equipamentos, perder identificadores ou produzir uma planilha aparentemente correta com atributos trocados. Esta solução separa a decisão sobre quais linhas cadastrar da interação com o Excel e da conferência final.

Os CSVs de entrada permanecem somente para leitura. Cada execução nova cria seus próprios arquivos, e o programa só anuncia conclusão após verificar os dados efetivamente gravados.

## Funcionalidades implementadas

- Leitura dos dois CSVs com contrato de colunas, codificação e delimitador definidos.
- Validação de IDs, campos obrigatórios, situações permitidas e unicidade da base original.
- Classificação das solicitações entre já cadastradas, repetidas na própria lista e novas válidas.
- Resumo no terminal e três pontos de autorização: seleção inicial, piloto e continuação, quando aplicáveis.
- Inserção de até três equipamentos no piloto e conferência antes da liberação do restante.
- Colagem tabular via área de transferência, preservando acentos e verificando a janela ativa.
- Salvamento pelo Excel, espera pela persistência e tentativa de “Salvar como” quando necessária.
- Retomada de cópia parcial compatível, sem reinserir o prefixo de equipamentos já conferido.
- Pastas de saída com número de versão e data local.
- Publicação de um XLSX final ordenado por ID, separado da cópia de trabalho.
- Verificação de SHA-256 dos CSVs e comparação integral dos cinco campos do XLSX.

Não há banco de dados, API, dashboard ou Machine Learning nesta versão.

## Decisões técnicas

| Decisão | Motivo e efeito |
|---|---|
| IDs tratados como texto | Preserva o identificador original e seus zeros à esquerda. |
| Classificação antes da GUI | Impede que a rotina visual receba linhas classificadas como duplicadas. |
| Prioridade para IDs já cadastrados | Uma solicitação existente é bloqueada mesmo que também se repita na lista recebida. |
| Primeira ocorrência de um ID inédito | Mantém uma seleção determinística na ordem das solicitações. |
| Cópia de trabalho separada do final | A retomada conserva a ordem de inserção; a entrega final pode ser ordenada. |
| Reabertura do XLSX | A conclusão depende do conteúdo salvo, não apenas de comandos enviados ao Excel. |
| Criação exclusiva de arquivos | Evita substituir silenciosamente resultados anteriores. |
| Mutex local do Windows na reserva de versões | Coordena a escolha do número entre processos da mesma sessão Windows; não autoriza operações gráficas simultâneas. |

A duplicidade é decidida pelo ID. O programa não faz uma conciliação comercial de atributos conflitantes entre solicitações com o mesmo ID: aplica a precedência acima.

## Tecnologias

| Recurso | Uso no projeto |
|---|---|
| Python | Funções de processamento, orquestração e interface de linha de comando. |
| Pandas | Leitura textual, classificação, seleção, concatenação e ordenação. |
| PyAutoGUI | Atalhos, ativação de janelas e interação assistida com o Excel. |
| Pyperclip | Transferência do bloco tabulado para a área de transferência. |
| Openpyxl | Criação das cópias e reabertura dos XLSX para conferência. |
| pathlib e argparse | Caminhos locais e opção de retomada. |
| hashlib | Impressões SHA-256 dos arquivos de entrada. |
| ctypes, datetime, re e time | Mutex Windows, identificação das execuções, validação de nomes e esperas operacionais. |

## Fluxo de execução

1. **Ler e validar:** localizar os CSVs ao lado de `Automação.py`, registrar hashes e conferir o contrato.
2. **Classificar:** comparar IDs, conciliar contagens e apresentar o resumo e uma amostra.
3. **Autorizar:** receber a decisão inicial antes de preparar uma nova saída.
4. **Preparar ou retomar:** criar uma cópia com os originais ou verificar uma cópia parcial existente.
5. **Executar o piloto:** após autorização específica, preencher até três novos equipamentos e conferir o XLSX.
6. **Autorizar a continuação:** retornar à janela do VS Code e aguardar a decisão no terminal.
7. **Completar e verificar:** inserir apenas os pendentes, salvar e comparar todas as linhas esperadas.
8. **Publicar:** conferir os hashes das entradas, ordenar por ID e criar/verificar o arquivo final.

Uma cópia já completa ou um lote sem novos equipamentos pode concluir sem passar pelas perguntas de piloto e continuação. Os checkpoints são aplicados quando a operação correspondente é necessária.

## Contrato dos dados

Os arquivos devem estar na mesma pasta do script:

- `equipamentos_cadastrados.csv`: cadastro de referência.
- `novos_equipamentos.csv`: solicitações, cuja ordem determina a primeira ocorrência de um ID novo.

A leitura utiliza `sep=";"`, `encoding="utf-8-sig"`, `dtype=str` e `keep_default_na=False`. São exigidas exatamente as cinco colunas abaixo, sem colunas extras ou cabeçalhos duplicados; a ordem física pode variar, pois o código reorganiza por nome.

| Coluna | Regra aplicada |
|---|---|
| `id_equipamento` | Texto não vazio, sem espaços nas extremidades; único no cadastro original. |
| `nome_equipamento` | Não pode ser uma string vazia. |
| `categoria` | Não pode ser uma string vazia. |
| `setor` | Não pode ser uma string vazia. |
| `situacao` | Exatamente `Disponível`, `Em uso` ou `Em manutenção`. |

A publicação final exige IDs no padrão `EQP` seguido de quatro dígitos, como `EQP0002` e `EQP0010`. Nesse formato, a ordenação textual crescente corresponde à ordem numérica do sufixo. IDs fora do padrão bloqueiam a publicação; não são corrigidos automaticamente.

O bloco enviado ao Excel rejeita campos com tabulação ou quebra de linha. Os campos não são limpos nem normalizados por suposição.

Os documentos do lote de referência registram 342 equipamentos originais e 259 solicitações: 35 já cadastradas, 24 repetições internas e 200 novas válidas, com resultado esperado de 542 equipamentos. **Esses números pertencem àquele lote e não são constantes do programa.** Consulte o [relatório histórico](planejamento/projeto/RELATORIO_STATUS_PROJETO.md) para o contexto das verificações.

## Ambiente e instalação

O fluxo atual depende de:

- Windows com sessão gráfica ativa.
- Microsoft Excel desktop instalado e associado a arquivos `.xlsx`.
- VS Code, com execução no terminal integrado.
- Python com suporte à sintaxe utilizada. As anotações `Path | None` exigem Python 3.10 ou posterior; isso não representa uma certificação de todas as combinações de Python e bibliotecas.
- Acesso de leitura às entradas e de escrita à pasta do projeto.

Não há arquivo de dependências com versões fixadas nem matriz de compatibilidade publicada. Os comandos abaixo instalam as dependências diretas; a compatibilidade deve ser conferida no ambiente escolhido.

No PowerShell:

```powershell
git clone https://github.com/ayrton-marquezin-venancio/automacao-planilha.git
cd automacao-planilha
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pandas openpyxl pyautogui pyperclip
```

O clone depende da permissão de acesso ao repositório. Usar o executável do ambiente diretamente dispensa ativar o ambiente virtual ou alterar a política de execução do PowerShell.

## Como executar

Abra a pasta do projeto no VS Code e utilize seu terminal integrado:

```powershell
.\.venv\Scripts\python.exe ".\Automação.py"
```

Confira o resumo e responda a cada confirmação:

| Resposta | Comportamento |
|---|---|
| `SIM`, `sim`, `Sim` e outras variações de caixa | Autoriza somente a etapa perguntada. |
| `NÃO`, `não`, `NAO`, `nao` e variações | Encerra normalmente, sem executar etapas posteriores. |
| Resposta vazia ou outro texto | Exibe uma orientação e aguarda nova resposta. |

Espaços nas extremidades da resposta são ignorados. A autorização inicial não libera automaticamente o piloto nem a continuação.

Antes de responder à continuação, selecione o terminal que está executando o script. A reativação da janela do VS Code não comprova que o painel interno correto recebeu foco. Durante o preenchimento, acompanhe a execução e evite interferir na janela do Excel. O `FAILSAFE` do PyAutoGUI permanece habilitado.

**Cancelamento:** antes da autorização inicial, nenhuma saída nova é criada. Depois da preparação ou do piloto, a cópia de trabalho é preservada e seu caminho é informado; o cancelamento não publica uma planilha parcial como resultado final.

O retorno `0` também é usado para cancelamento normal. Portanto, confira a mensagem de conclusão e a existência do final verificado, em vez de tratar apenas o código de saída como prova de cadastro concluído.

## Retomada de uma execução

Use o caminho real da **cópia de trabalho**, mantendo os mesmos CSVs usados na execução original:

```powershell
.\.venv\Scripts\python.exe ".\Automação.py" --retomar ".\saidas\Planilha Versão 1 - AAAA-MM-DD\equipamentos_atualizados_IDENTIFICADOR.xlsx"
```

O exemplo contém marcadores: substitua a data, a versão e o identificador pelos valores da execução existente. Não utilize `equipamentos_atualizados.xlsx` como arquivo de retomada.

A cópia precisa estar diretamente em uma pasta de versão válida dentro de `saidas`. O código confere originais, atributos e sequência dos novos já salvos; apenas um prefixo compatível da seleção é aceito. A retomada não cria outro número de versão.

**Limitação operacional atual:** quando três ou mais novos equipamentos já estão salvos e ainda há pendentes, o fluxo pula o piloto e tenta ativar uma janela existente do arquivo. Nessa situação, abra manualmente a cópia correta no Excel e retorne ao terminal do VS Code antes de iniciar a retomada. A rotina não abre essa janela automaticamente nesse ramo.

Os hashes são capturados a cada chamada do programa, não em um manifesto persistente de aprovação. A retomada confere o conteúdo contra as entradas atuais; não comprova, por si só, que os bytes das fontes permaneceram iguais entre duas execuções.

## Arquivos produzidos

```text
saidas/
└── Planilha Versão N - AAAA-MM-DD/
    ├── equipamentos_atualizados_<identificador-UTC>.xlsx
    └── equipamentos_atualizados.xlsx
```

- **Cópia de trabalho:** originais seguidos dos novos na ordem de inserção; pode estar parcial e é usada na retomada.
- **Planilha final:** todos os equipamentos em ordem crescente de ID, com os atributos preservados. Só é publicada após as verificações.
- **Número da pasta:** maior número válido existente mais um, sem reiniciar a cada mudança de data.
- **Data da pasta:** data local do computador; o identificador no nome da cópia usa UTC.
- **Final existente:** não é sobrescrito. No ramo de conclusão de uma retomada, só é aceito se corresponder ao resultado ordenado esperado.

Excluir pastas de saída pode permitir reutilização de números, pois a sequência é calculada a partir das pastas existentes. Preserve os resultados que precisam de histórico ou retomada.

Essas versões de planilhas são independentes dos **commits e tags do Git**, que registram a evolução do código. Esta publicação inclui as duas planilhas da pasta `Planilha Versão 1`; futuras saídas continuam ignoradas pelo Git.

## Qualidade, evidências e limites

O código implementa verificações de:

- Cabeçalho, campos e IDs antes da interação visual.
- Conciliação das categorias das solicitações.
- IDs únicos e ausência de interseção entre selecionados e cadastro original.
- Conteúdo completo da cópia parcial ou final, incluindo ordem quando exigida.
- Tipos textuais dos IDs após reabrir o XLSX.
- Preservação dos CSVs por SHA-256 dentro da execução.
- Janela ativa, salvamento e manutenção do `FAILSAFE`.

Os [documentos de planejamento](planejamento/README.md) preservam registros datados de testes e revisões. Eles representam evidências históricas dos respectivos escopos, não uma certificação da versão atual em qualquer computador.

A suíte de testes foi retirada do versionamento atual por decisão do autor e preservada no ambiente local. Ela não acompanha um clone desta revisão, mas permanece nos commits anteriores. Não há pipeline de integração contínua configurado nesta versão.

A reorganização documental de 04/11/2026 não executou a automação nem revalidou a interface gráfica. O ensaio histórico de foco da terceira confirmação permaneceu incompleto após uma interrupção por fail-safe; os detalhes estão nas [tarefas de autorizações](planejamento/autorizacoes-piloto-continuacao/tasks.md).

Outras limitações:

- A entrada ainda depende de dois CSVs com nomes e contrato fixos; XLSX não é aceito como fonte genérica.
- A restauração de foco exige uma janela identificada como Visual Studio Code; outros terminais ou títulos personalizados podem ser bloqueados.
- Diálogos, foco, associação de arquivos e tempos de resposta do Excel dependem do ambiente.
- Uma nova execução parte novamente dos CSVs; o final anterior não atualiza automaticamente o cadastro de referência.
- O mutex de numeração não torna seguro executar duas automações gráficas simultaneamente.
- Não há medição publicada de ganho de produtividade nem garantia de funcionamento sem supervisão.

## Estrutura do repositório

```text
automacao-planilha/
├── Automação.py
├── equipamentos_cadastrados.csv
├── novos_equipamentos.csv
├── README.md
├── saidas/
│   └── Planilha Versão 1 - 2026-11-04/
│       ├── equipamentos_atualizados.xlsx
│       └── equipamentos_atualizados_20261104T033307402854Z.xlsx
├── .gitignore
└── planejamento/
    ├── README.md
    ├── projeto/
    ├── confirmacao-terminal/
    ├── autorizacoes-piloto-continuacao/
    ├── versionamento-saidas/
    └── ordenacao-equipamentos/
```

`tests/` permanece no computador de desenvolvimento e não acompanha esta publicação; os testes continuam no histórico anterior. O repositório inclui as duas planilhas como evidência da Versão 1. Outras saídas e caches não são adicionados automaticamente.

Consulte o [índice de planejamento](planejamento/README.md) para a ordem de leitura, as diferenças entre registros históricos e código atual e o mapa dos documentos reorganizados.

## Autor

**Ayrton M. Venancio**

## Próxima evolução: entradas de equipamentos mais flexíveis

O próximo passo é tornar o preenchimento mais automatizado, permitindo atualizar a tabela atual de equipamentos a partir de diferentes planilhas recebidas, em vez de depender exclusivamente de uma fonte fixa de solicitações.

Essa evolução ainda **não está implementada**. Ela deverá contemplar seleção do arquivo de entrada, definição dos formatos suportados, mapeamento das colunas e validação de compatibilidade, mantendo a preservação dos IDs, o tratamento de duplicidades, as autorizações e a conferência final.

O objetivo é ampliar a variedade de planilhas aceitas mediante um contrato validado, sem presumir que qualquer planilha arbitrária possa ser interpretada corretamente.
