# PRD — Automação de Cadastro de Equipamentos

| Campo | Valor |
|---|---|
| Versão | 1.0 — proposta para validação |
| Data | 30/10/2026 |
| Responsável pelo produto | A definir |
| Estado | Requisitos documentados; implementação pendente |
| Diretório de trabalho | `7 - Automação de Cadastro de Equipamentos/` |
| Arquivo de implementação | `Automação.py` |
| Fontes | `Cadastro_de_Equipamentos_Introducao.pdf`, `equipamentos_cadastrados.csv`, `novos_equipamentos.csv` |

## 1. Visão geral

Automatizar a atualização local de um cadastro patrimonial. O programa deve comparar solicitações recebidas com equipamentos já cadastrados, selecionar apenas a primeira ocorrência de cada equipamento inédito e inseri-la em uma cópia de trabalho no Excel por automação visual. O resultado previsto para o lote fornecido é `equipamentos_atualizados.xlsx` com 542 equipamentos de IDs únicos.

O projeto tem finalidade prática de RPA com Python, pandas, PyAutoGUI e Excel. A rotina ainda não foi implementada: `Automação.py` contém apenas imports.

## 2. Problema, objetivos e limites

### Problema

A conferência manual de solicitações e a digitação no cadastro principal consomem tempo e podem registrar o mesmo patrimônio mais de uma vez.

### Objetivos

1. Classificar todas as solicitações por comparação efetiva de IDs.
2. Impedir a inserção de equipamentos já cadastrados e de repetições internas.
3. Atualizar uma cópia de trabalho no Excel, preservando os dois CSVs originais.
4. Reabrir e conferir o XLSX salvo antes de considerar o processamento concluído.

### Fora do escopo da V1

Banco de dados, API, sistema externo de cadastro e interface web. O uso do PyAutoGUI é intencional para exercitar automação visual, mesmo que pandas pudesse produzir um arquivo consolidado diretamente.

## 3. Usuário e fluxo de trabalho

**Usuário principal:** analista de controle patrimonial que recebe solicitações, confere duplicidades e mantém o cadastro atualizado.

1. O analista disponibiliza os dois CSVs no diretório do projeto.
2. A rotina lê e valida as entradas, mantendo IDs como texto.
3. A rotina apresenta a classificação e as contagens para conferência antes da digitação.
4. Uma cópia de trabalho com os registros originais é aberta no Excel.
5. O PyAutoGUI insere os equipamentos inéditos; um lote pequeno é conferido antes do lote completo.
6. A rotina salva, reabre e valida `equipamentos_atualizados.xlsx`.

## 4. Entradas e contrato de dados

| Fonte | Linhas de dados verificadas | Colunas reais |
|---|---:|---|
| `equipamentos_cadastrados.csv` | 342 | `id_equipamento`, `nome_equipamento`, `categoria`, `setor`, `situacao` |
| `novos_equipamentos.csv` | 259 | `id_equipamento`, `nome_equipamento`, `categoria`, `setor`, `situacao` |

Ambos usam separador `;` e codificação UTF-8 com BOM. `id_equipamento` é texto e chave de comparação. Cada linha representa um equipamento físico. As situações observadas são `Disponível`, `Em uso` e `Em manutenção`.

**Divergência entre briefing e arquivo real:** o PDF descreve sete colunas na base de solicitações, incluindo `status_cadastro` e `motivo_duplicidade`. O CSV disponível possui cinco colunas. A V1 deve calcular classificação e motivo em memória, sem depender dessas colunas e sem modificar o CSV. A forma de apresentar ou exportar essa classificação ainda requer decisão do usuário.

## 5. Regras de negócio

| ID | Regra |
|---|---|
| RN01 | Se o ID solicitado já existir no cadastro original, classificar como `Equipamento Duplicado`, motivo `Já cadastrado na base original`, e não inserir. |
| RN02 | Se um ID ausente no cadastro original aparecer mais de uma vez nas solicitações, aceitar apenas a primeira ocorrência; classificar as seguintes como `Equipamento Duplicado`, motivo `Repetido na base de novos equipamentos`. |
| RN03 | Uma primeira ocorrência ausente do cadastro original é `Novo Equipamento` e pode seguir para inserção. |
| RN04 | A classificação deve resultar da comparação dos IDs, sem confiar em rótulos prévios. |
| RN05 | Os dois CSVs originais não podem ser alterados nem sobrescritos. |
| RN06 | Uma retomada após falha deve conferir os IDs efetivamente salvos antes de inserir novamente. |

Para o lote atual, a análise independente encontrou 342 IDs únicos na base original e, entre 259 solicitações, 35 já cadastradas, 24 repetições internas e 200 novos válidos. Não há IDs vazios nem atributos contraditórios para um mesmo ID. Esses números são referências de aceite para este lote, não constantes a serem impostas pelo código.

## 6. Requisitos funcionais

| ID | Prioridade | Requisito | Critério de aceite |
|---|---|---|---|
| RF01 | Essencial | Localizar e ler os dois CSVs com `;`, UTF-8 com BOM e IDs textuais. | Exibir 342 e 259 linhas, colunas esperadas e IDs preservados. |
| RF02 | Essencial | Validar campos obrigatórios e integridade da chave. | Interromper com motivo claro se faltar arquivo, coluna ou ID. |
| RF03 | Essencial | Identificar IDs já cadastrados. | Classificar 35 solicitações do lote atual nessa condição. |
| RF04 | Essencial | Detectar repetições internas e manter a primeira ocorrência válida. | Classificar 24 repetições e selecionar 200 IDs inéditos únicos. |
| RF05 | Essencial | Apresentar resumo da seleção antes da automação visual. | Permitir conferir 259 = 35 + 24 + 200 antes de abrir a etapa de preenchimento. |
| RF06 | Essencial | Criar cópia de trabalho com os 342 registros originais. | A cópia contém a base original; os CSVs não mudam. |
| RF07 | Essencial | Inserir somente novos válidos por meio do Excel e PyAutoGUI. | Um lote pequeno é conferido; nenhuma linha bloqueada é inserida. |
| RF08 | Essencial | Salvar e reabrir o XLSX final para verificação. | Há 542 linhas de dados e 542 IDs únicos, com os 342 originais e 200 novos. |
| RF09 | Importante | Registrar progresso, falhas e destino do arquivo de saída. | Após interrupção, é possível identificar o que foi gravado e evitar repetição. |

## 7. Requisitos não funcionais

- **Segurança operacional:** manter `pyautogui.FAILSAFE` habilitado; conferir a janela ativa antes de cliques, digitação ou atalhos.
- **Confiabilidade:** evitar dependência exclusiva de coordenadas fixas; validar a posição da próxima linha antes de cada continuação.
- **Integridade:** preservar tipos textuais dos IDs e não sobrescrever os CSVs.
- **Rastreabilidade:** distinguir a saída da execução atual de arquivos antigos e registrar as contagens e falhas.
- **Recuperação:** após falha, inspecionar o XLSX parcial antes de repetir uma operação.
- **Verificação independente:** reabrir o XLSX com `openpyxl`; a aparência da janela do Excel não basta como prova do resultado.

## 8. Solução técnica proposta

| Componente | Responsabilidade |
|---|---|
| Python + `pathlib` | Orquestração e caminhos locais. |
| `pandas` | Leitura, comparação, classificação e seleção de registros. |
| `PyAutoGUI` | Controle visual da janela do Excel. |
| `openpyxl` | Inspeção do XLSX salvo e validação de células e IDs. |
| `Automação.py` | Ponto único da implementação solicitado para este projeto. |

O processamento deve separar a fase de seleção da fase de digitação. A digitação só começa depois de conferir a seleção de 200 novos IDs no lote atual.

## 9. Marcos e critérios de conclusão

| Marco | Resultado observável |
|---|---|
| M1 — Ambiente e leitura | Os arquivos são localizados e lidos sem modificação; contagens 342 e 259. |
| M2 — Classificação | Todas as 259 solicitações são conciliadas: 35 já existentes, 24 repetições e 200 novas. |
| M3 — Cópia de trabalho | Planilha de trabalho contém os 342 registros atuais. |
| M4 — Automação assistida | Lote pequeno validado antes de inserir os demais novos equipamentos. |
| M5 — Salvamento e conferência | XLSX reaberto com 542 linhas de dados, 542 IDs únicos e nenhum registro bloqueado inserido como nova linha. |
| M6 — Revisão | Entradas preservadas, resultado reproduzível e falhas investigadas. |

O cronograma e o responsável por cada marco permanecem **a definir**.

## 10. Métricas de sucesso

- **Conciliação:** 100% das solicitações classificadas exatamente uma vez.
- **Unicidade:** nenhum ID repetido no XLSX final.
- **Preservação:** os dois CSVs permanecem idênticos aos originais após a execução.
- **Exatidão no lote atual:** 200 novos inseridos, 59 solicitações bloqueadas e 542 equipamentos finais.
- **Tempo:** comparar duração manual e automatizada em condição equivalente; meta numérica ainda **a definir**.
- **Falhas operacionais:** registrar inserções que precisaram de correção ou retomada.

## 11. Riscos e decisões pendentes

| Tema | Risco / decisão necessária |
|---|---|
| Excel e PyAutoGUI | Confirmar versão do Excel, resolução da tela e condições da máquina onde ocorrerá a execução. |
| Classificação | Definir se motivos serão mostrados apenas no resumo ou também em arquivo de saída separado. |
| Confirmação antes da digitação | Definir como o analista autorizará o início do lote após revisar a seleção. |
| Saída anterior | Definir convenção para identificar novas execuções sem confundir ou sobrescrever resultados antigos. |
| Interrupção | Definir procedimento de retomada a partir do XLSX parcial validado. |

## 12. Evolução futura

Depois do aceite da V1, avaliar histórico de execuções e retomada mais automatizada. Essas capacidades não integram os critérios de conclusão atuais.
