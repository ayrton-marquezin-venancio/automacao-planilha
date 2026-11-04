# SPEC — Automação de Cadastro de Equipamentos

| Campo | Definição |
|---|---|
| Versão | 1.0 — proposta técnica para validação |
| Data | 30/10/2026 |
| Estado | Especificado; implementação não iniciada |
| Documento de origem | [PRD.md](PRD.md) |
| Código previsto | `../../Automação.py` |
| Entradas | `../../equipamentos_cadastrados.csv`, `../../novos_equipamentos.csv` |
| Saída prevista | `equipamentos_atualizados.xlsx` em local a definir antes da implementação |

## 1. Visão geral e fronteira da solução

### 1.1 Resultado esperado

Uma execução local lê os dois CSVs, classifica cada solicitação pela chave `id_equipamento`, apresenta a seleção ao analista, prepara uma cópia de trabalho com o cadastro original, insere no Excel apenas os equipamentos inéditos por automação visual e reabre o XLSX para conferir o resultado. O lote disponível contém 342 cadastros originais, 259 solicitações e 200 equipamentos inéditos; o XLSX esperado contém 542 IDs únicos.

### 1.2 Fronteira

- **Dentro:** arquivos locais, Python, pandas, Excel, PyAutoGUI, verificação com openpyxl e operação assistida.
- **Fora:** banco de dados, API, sistema patrimonial externo, interface web e cadastro direto apenas por pandas/openpyxl sem a etapa visual de PyAutoGUI.
- **Invariante:** os CSVs são entradas somente para leitura. Nenhuma rotina pode renomeá-los, movê-los ou sobrescrevê-los.

### 1.3 Estado do projeto

O arquivo `../../Automação.py` contém somente imports de `pandas`, `pyautogui` e `time`. Esta SPEC descreve o comportamento a implementar; nenhum marco de execução ou aceite foi comprovado por ela.

## 2. Problema, objetivos e critérios de valor

O processo manual compara solicitações e copia linhas para uma planilha, com risco de duplicar patrimônios ou deixar de cadastrar equipamentos novos. A automação deve reduzir a digitação repetitiva mantendo uma decisão verificável para cada solicitação.

| Objetivo do PRD | Comportamento exigido | Evidência de aceite |
|---|---|---|
| Classificar todas as solicitações | Cada linha recebe exatamente uma categoria e um motivo quando bloqueada. | Contagens reconciliadas com as 259 linhas lidas. |
| Evitar duplicidade | ID existente e ocorrências internas posteriores não seguem para digitação. | Interseção entre IDs selecionados e originais vazia; IDs selecionados únicos. |
| Preservar entradas | Leitura sem escrita nos CSVs. | Hash ou comparação de bytes antes e depois da execução. |
| Verificar a saída real | Reabrir o XLSX salvo e comparar conteúdo com originais + novos selecionados. | 542 linhas de dados e 542 IDs únicos no lote atual. |

Os números acima são referências do lote presente. A lógica deve derivar as contagens dos arquivos lidos e falhar quando a reconciliação não fechar; não deve codificar 342, 259, 200 ou 542 como condição universal de funcionamento.

## 3. Usuários e cenários independentes

### US01 — Conferir e classificar solicitações (P1)

Como analista, quero saber quais equipamentos já existem e quais são inéditos antes de abrir o Excel, para evitar registros duplicados.

**Verificação independente:** executar somente a fase de leitura e classificação, sem automação visual, e conferir resumo e conjunto selecionado.

1. **Dado** o lote atual, **quando** as bases forem comparadas, **então** 35 linhas serão classificadas como já cadastradas, 24 como repetição interna e 200 como novas válidas.
2. **Dado** um ID novo repetido na lista de solicitações, **quando** ocorrer pela primeira vez, **então** a primeira linha será selecionada e as seguintes bloqueadas com motivo de repetição interna.
3. **Dado** um ID que já exista no cadastro original, **quando** aparecer nas solicitações, **então** será bloqueado independentemente da posição na lista nova.

### US02 — Preparar e inserir em cópia de trabalho (P2)

Como analista, quero confirmar a seleção e acompanhar a digitação no Excel, para atualizar o cadastro sem alterar as fontes.

**Verificação independente:** preparar a cópia com as 342 linhas originais e executar um lote pequeno autorizado, conferindo visualmente IDs e posição da próxima linha. A verificação completa depende do aceite da US01.

1. **Dada** a seleção conferida, **quando** começar a etapa visual, **então** a cópia de trabalho conterá primeiro todos os originais e somente os IDs selecionados serão enviados ao Excel.
2. **Dado** que a janela ativa não seja a planilha correta ou que a posição de escrita seja incerta, **quando** a inserção for solicitada, **então** a rotina não prosseguirá silenciosamente.

### US03 — Salvar, conferir e retomar com segurança (P3)

Como analista, quero validar o arquivo salvo e identificar o progresso após uma falha, para não repetir cadastros ou aceitar uma saída incompleta.

**Verificação independente:** reabrir um XLSX produzido pela etapa visual e confrontar IDs e atributos com o conjunto esperado; em uma execução interrompida, comparar o arquivo parcial com os IDs pendentes antes da retomada.

1. **Dado** o lote completo inserido, **quando** o XLSX for reaberto, **então** conterá 342 originais e 200 inéditos, total de 542 IDs únicos.
2. **Dado** um erro antes do fim, **quando** a rotina for retomada, **então** os IDs já presentes no XLSX parcial serão identificados antes de qualquer nova digitação.

## 4. Entradas e contrato de dados

### 4.1 Arquivos e leitura

| Arquivo | Papel | Linhas atuais | Formato constatado |
|---|---|---:|---|
| `../../equipamentos_cadastrados.csv` | Cadastro de referência | 342 | CSV `;`, UTF-8 com BOM, 5 colunas |
| `../../novos_equipamentos.csv` | Solicitações ordenadas | 259 | CSV `;`, UTF-8 com BOM, 5 colunas |

As cinco colunas, nesta ordem lógica, são `id_equipamento`, `nome_equipamento`, `categoria`, `setor` e `situacao`. A rotina deve validar seus nomes; a ordem física pode ser tratada pelo nome da coluna. Ler os campos como texto, desabilitando conversões automáticas de ID e de valores vazios que alterem a interpretação. A ordem das linhas em `novos_equipamentos.csv` determina qual ocorrência interna é a primeira.

### 4.2 Validação de entrada

1. Confirmar que os dois caminhos apontam para arquivos legíveis.
2. Confirmar separador e cabeçalhos; interromper em caso de coluna obrigatória ausente ou duplicada.
3. Preservar o texto exato de cada ID para comparação e exportação. Não converter para número nem remover zeros à esquerda. Uma política de espaços laterais em IDs exige decisão explícita; nenhuma normalização silenciosa é permitida.
4. Bloquear o processamento visual se houver ID vazio ou duplicado na base original. Outros campos vazios ou valores de `situacao` fora dos observados exigem classificação/decisão antes de cadastrar, sem preenchimento por suposição.
5. Registrar quantidade de linhas por arquivo e uma impressão digital dos bytes antes da operação, para comparar depois.

**Divergência documentada:** o PDF descreve sete colunas para as solicitações, mas o CSV real contém cinco. `status_cadastro` e `motivo_duplicidade` são resultados calculados em memória. Eles não são pré-requisitos de entrada nem devem ser escritos no CSV original.

### 4.3 Entidades em memória

- **Equipamento original:** cinco campos recebidos, ID único no cadastro de referência.
- **Solicitação:** cinco campos recebidos, posição original na lista e classificação calculada.
- **Decisão de classificação:** `id_equipamento`, posição de origem, estado (`novo_valido` ou `duplicado`) e motivo (`ja_cadastrado`, `repetido_na_lista` ou nenhum). Os rótulos de apresentação seguem o PRD.
- **Resultado de execução:** caminhos das fontes e da saída, contagens por classe, IDs selecionados, progresso da inserção e resultado da verificação do XLSX. O formato persistente desse registro permanece a definir.

## 5. Regras de classificação e seleção

### 5.1 Ordem obrigatória

Para cada solicitação na ordem física do CSV:

1. Se `id_equipamento` estiver no conjunto de IDs do cadastro original, aplicar **RN01**: `Equipamento Duplicado`, motivo `Já cadastrado na base original`.
2. Caso contrário, se o ID já tiver sido aceito antes na própria lista, aplicar **RN02**: `Equipamento Duplicado`, motivo `Repetido na base de novos equipamentos`.
3. Caso contrário, aplicar **RN03**: `Novo Equipamento` e adicionar o ID ao conjunto de novos aceitos.

Essa precedência evita classificar um equipamento já cadastrado como mero repetido interno. As decisões devem resultar da comparação dos IDs (**RN04**), nunca de rótulos fornecidos ou de uma contagem esperada.

### 5.2 Invariantes verificáveis

- Cada linha de solicitação tem exatamente uma classificação.
- `total_solicitacoes = ja_cadastrados + repetidos_na_lista + novos_validos`.
- IDs de `novos_validos` são únicos e não pertencem aos IDs originais.
- O conjunto final esperado é a união dos IDs originais com os novos válidos.
- A ordem de inserção dos novos preserva a primeira ocorrência na lista recebida.
- O cadastro original permanece na saída com os mesmos cinco campos e valores.

No lote atual: `259 = 35 + 24 + 200` e `342 + 200 = 542`. A análise de referência encontrou 342 IDs originais únicos, 259 solicitações e nenhum atributo contraditório para um mesmo ID. A rotina precisa recalcular essas condições a cada execução.

## 6. Requisitos funcionais detalhados

| PRD | Contrato técnico | Evidência mínima |
|---|---|---|
| RF01 | Resolver caminhos a partir da pasta do script ou de um caminho explícito; ler `;`, UTF-8 com BOM e `dtype` textual. | Contagens, cabeçalhos e amostra sem mudança dos IDs. |
| RF02 | Validar arquivos, cinco colunas, IDs não vazios e unicidade do cadastro original antes de classificar. | Erro específico interrompe a fase visual. |
| RF03 | Construir conjunto de IDs originais e testar cada solicitação contra ele. | 35 bloqueios RN01 no lote atual. |
| RF04 | Manter conjunto de novos aceitos em ordem e bloquear ocorrências posteriores. | 24 bloqueios RN02 e 200 selecionados no lote atual. |
| RF05 | Exibir totais, motivos e uma amostra de IDs por classe; exigir checkpoint de revisão antes da fase visual. | Analista consegue conferir a reconciliação antes de digitar. |
| RF06 | Criar XLSX de trabalho separado com cabeçalho e os registros originais. | Reabertura mostra 342 linhas originais no lote atual. |
| RF07 | Validar janela e posição, testar lote pequeno e inserir somente seleção confirmada por PyAutoGUI. | Conferência de IDs e valores do lote piloto e do lote completo. |
| RF08 | Salvar, reabrir com openpyxl e comparar contagem, conjunto de IDs e atributos com o resultado esperado. | 542 IDs únicos, originais preservados e novos corretos. |
| RF09 | Informar saída, estágio, contagens e falha; na retomada, ler o XLSX parcial e comparar os IDs. | Nenhum ID já gravado é reinserido. |

## 7. Requisitos não funcionais e proteção operacional

### 7.1 Integridade e rastreabilidade

- Operar os CSVs em modo de leitura e comparar hashes antes/depois (**RN05**).
- Nunca usar o XLSX de uma execução anterior como comprovação da atual. Identificar o caminho da saída no início e no resumo.
- Não considerar sucesso apenas porque o PyAutoGUI terminou: a reabertura e a comparação do XLSX são obrigatórias.
- Manter IDs como texto também no Excel; a verificação deve comparar strings, inclusive zeros à esquerda quando houver.

### 7.2 Automação visual

- Manter `pyautogui.FAILSAFE` habilitado.
- Confirmar que a janela ativa é a planilha de trabalho correta antes de digitar ou enviar atalhos.
- Validar a célula/linha inicial e a progressão; parar quando foco ou posição forem incertos.
- Não depender exclusivamente de coordenadas fixas. Qualquer coordenada configurada deve ser confirmada no ambiente real.
- Validar um lote pequeno antes do lote completo. Tamanho e forma do checkpoint dependem de decisão do operador.
- Em falha, interromper a digitação e conferir o XLSX efetivamente salvo antes de retomar (**RN06**).

### 7.3 Desempenho e ambiente

O projeto visa reduzir trabalho manual, mas não há meta de duração nem configuração de máquina aprovadas. A medição deve registrar tempo de referência manual e tempo da execução automatizada em condições comparáveis. Excel instalado, versão e resolução de tela continuam pendentes de confirmação.

## 8. Desenho técnico e interfaces

### 8.1 Componentes previstos

| Componente | Responsabilidade | Limite |
|---|---|---|
| `../../Automação.py` | Orquestrar fases e manter funções separadas para leitura, validação, classificação, preparação, inserção e verificação. | Único arquivo de código previsto no PRD. |
| `pathlib` | Resolver caminhos locais de entrada e saída. | Não alterar os arquivos de entrada. |
| `pandas` | Ler CSVs e classificar solicitações. | Não usar rótulos prontos como decisão. |
| `openpyxl` | Preparar cópia de trabalho e reabrir/verificar XLSX. | Não substituir a etapa de inserção visual exigida. |
| `PyAutoGUI` | Interagir com o Excel depois da aprovação da seleção. | Preservar FAILSAFE e validar foco/posição. |

Versões de Python, pandas, PyAutoGUI, openpyxl e Excel ainda não foram fixadas pelo PRD. Devem ser registradas ao preparar o ambiente; esta SPEC não inventa versões.

### 8.2 Fluxo e pontos de bloqueio

```text
CSV original + CSV de solicitações
  → leitura e validação do contrato
  → classificação integral e reconciliação
  → checkpoint do analista: seleção aprovada?
  → criação de cópia XLSX com originais
  → confirmação de Excel, janela e posição
  → lote piloto e conferência
  → inserção do restante por PyAutoGUI
  → salvamento e reabertura do XLSX
  → comparação integral e resultado da execução
```

Falha em leitura, contrato, reconciliação, checkpoint, foco ou verificação impede declarar conclusão. A política de conservar, substituir ou versionar um XLSX parcial depende da decisão de saída e retomada na seção 11.

### 8.3 Contrato da saída

`equipamentos_atualizados.xlsx` deve conter no mínimo uma planilha de cadastro com os mesmos cinco campos das entradas. Os 342 originais ocupam a parte inicial; os 200 novos válidos do lote atual seguem em ordem de primeira ocorrência. Se forem adicionadas colunas ou abas de auditoria, isso exige decisão explícita, pois não faz parte do contrato mínimo.

Na reabertura, comparar tanto os IDs quanto os cinco atributos de cada linha esperada. Conferir número de linhas, ausência de IDs duplicados e ausência de IDs bloqueados como inserções adicionais. A posição e o formato de qualquer relatório técnico separado permanecem a definir.

## 9. Marcos, verificação e aceite

| Marco do PRD | Verificação prevista | Condição de avanço |
|---|---|---|
| M1 — Ambiente e leitura | Dois CSVs encontrados, cabeçalhos e tipos preservados, contagens conferidas. | Contrato de entrada válido. |
| M2 — Classificação | Todas as linhas têm destino; totais reconciliados; seleção única e sem interseção com originais. | Revisão do analista antes da etapa visual. |
| M3 — Cópia de trabalho | XLSX reaberto com todos os registros originais. | Cópia identificada e independente dos CSVs. |
| M4 — Inserção assistida | Lote piloto conferido; foco e progressão verificados. | Operador libera continuação. |
| M5 — Salvamento | XLSX final reaberto e comparado com união esperada. | Todas as verificações de contagem, IDs e atributos passam. |
| M6 — Revisão | Hashes originais inalterados, falhas documentadas e nova execução avaliada sem reinserção indevida. | Aceite do usuário. |

### Cenários de borda a verificar

1. Arquivo ausente, ilegível, cabeçalho diferente ou codificação inesperada: informar a causa e não iniciar o Excel.
2. ID vazio ou duplicado no cadastro original: bloquear a seleção até investigação.
3. ID presente na base original e repetido na nova: aplicar precedência de RN01 em todas as ocorrências.
4. ID inédito repetido na lista nova: selecionar apenas a primeira ocorrência.
5. Fonte vazia: apresentar contagens reais e não criar uma saída enganosa.
6. Excel errado em foco, célula inicial inadequada ou FAILSAFE acionado: interromper sem afirmar conclusão.
7. Saída parcial ou já existente: identificar os IDs gravados antes de qualquer retomada ou substituição.
8. Saída com contagem correta, mas atributos trocados: reprovar a verificação integral.

## 10. Métricas e critérios mensuráveis

| ID | Métrica | Meta / método |
|---|---|---|
| SC01 | Conciliação das solicitações | 100% das linhas classificadas exatamente uma vez; soma das classes igual ao total lido. |
| SC02 | Unicidade do XLSX | Zero IDs duplicados após reabrir o arquivo. |
| SC03 | Preservação das fontes | Hash de cada CSV igual ao registrado antes do processamento. |
| SC04 | Exatidão do lote atual | 35 já cadastrados, 24 repetidos internos, 200 novos e 542 IDs finais; todos derivados dos dados. |
| SC05 | Integridade de atributos | Cada ID final conserva os cinco campos esperados da origem selecionada. |
| SC06 | Tempo e falhas | Registrar tempos e incidentes; meta de redução e limite de falhas permanecem a definir. |

## 11. Riscos, pressupostos e decisões pendentes

### Pressupostos de implementação

- O analista dispõe de Excel desktop e acompanha a fase visual.
- A ordem física do CSV de solicitações define a primeira ocorrência de cada ID novo.
- O XLSX de cadastro mantém as cinco colunas das bases; classificação e motivo são dados de controle, não campos obrigatórios nessa planilha.
- Um lote piloto e um checkpoint explícito são necessários antes de inserir tudo, embora a interface exata ainda não esteja definida.

### Decisões que exigem validação antes da fase correspondente

| ID | Decisão pendente | Impacto |
|---|---|---|
| D01 | Versões do Python, bibliotecas e Excel; resolução e escala da tela. | Compatibilidade e calibração do PyAutoGUI. |
| D02 | Como mostrar/guardar `status_cadastro` e `motivo_duplicidade`: resumo na tela ou saída separada. | Rastreabilidade da classificação sem alterar os CSVs. |
| D03 | Como o analista aprova a seleção e o lote piloto; qual tamanho do piloto. | Ponto de controle antes da inserção completa. |
| D04 | Pasta e convenção da saída para distinguir execuções, evitar sobrescrita e tratar XLSX já existente. | Integridade e identificação do resultado atual. |
| D05 | Como salvar progresso e retomar um XLSX parcial validado. | Prevenção de reinserção após falha. |
| D06 | Política para espaços em IDs, campos não ID vazios e situações fora do conjunto observado. | Tratamento de dados futuros sem correção silenciosa. |
| D07 | Responsável, cronograma e meta de economia de tempo. | Planejamento e avaliação de benefício. |

Enquanto essas decisões não forem tomadas, as partes dependentes permanecem pendentes; a classificação em memória pode ser especificada e desenvolvida de forma independente.

## 12. Evolução futura e rastreabilidade

Histórico persistente de execuções e retomada mais automatizada são possibilidades posteriores ao aceite da V1. Não são condições para concluir esta versão.

| Fonte no PRD | Seções desta SPEC |
|---|---|
| 1. Visão geral | 1, 8 |
| 2. Problema, objetivos e limites | 2, 1.2 |
| 3. Usuário e fluxo | 3, 8.2 |
| 4. Entradas e contrato | 4 |
| 5. Regras de negócio | 5, 7 |
| 6. Requisitos funcionais | 6, 9 |
| 7. Requisitos não funcionais | 7 |
| 8. Solução técnica | 8 |
| 9. Marcos e critérios | 9 |
| 10. Métricas | 10 |
| 11. Riscos e decisões | 11 |
| 12. Evolução futura | 12 |
