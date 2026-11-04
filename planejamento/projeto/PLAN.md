# Cadastro de Equipamentos Implementation Plan

**Estado em 30/10/2026:** código das Tasks 1–6 implementado em `Automação.py`; 28 testes automatizados passaram. Com autorização limitada ao piloto, o Excel recebeu 3 equipamentos e o arquivo `saidas/execucao_20261030T232132834608Z/equipamentos_atualizados_20261030T232132834608Z_piloto.xlsx` foi reaberto e validado: 342 originais + 3 novos, cinco atributos iguais às fontes e hashes dos CSVs inalterados. O atalho Ctrl+S não persistiu a colagem neste ambiente; o piloto foi salvo pelo diálogo Salvar como. O código agora tenta esse diálogo se o salvamento normal não for confirmado, mas esse fallback ainda não foi testado em nova execução visual. Faltam autorização para os 197 registros restantes, execução integral e validação dos 542 registros; o resultado final não foi aceito.

> **Para execução:** use `$executing-plans` tarefa por tarefa; `$subagent-driven-development` é alternativa se houver revisão independente por tarefa. Marque os passos concluídos com `- [x]`. Este documento planeja a implementação; nenhuma tarefa foi executada.

**Goal:** Implementar em `Automação.py` a classificação de solicitações e a atualização assistida de uma cópia do cadastro no Excel, com verificação integral do XLSX salvo.

**Architecture:** Separar funções puras de leitura, validação e classificação da automação visual. A camada visual recebe somente os 200 novos válidos do lote atual após um checkpoint; a saída é reaberta para comparação de IDs e atributos. A orquestração fica em `main()` protegida por `if __name__ == "__main__"` para permitir testes sem abrir o Excel.

**Tech Stack:** Python, `pathlib`, `hashlib`, `pandas`, `openpyxl`, `pyautogui`; `pytest` e `unittest.mock` apenas para testes. Versões de Python, bibliotecas e Excel serão registradas na primeira tarefa, sem impor versões não definidas na SPEC.

**Spec:** [SPEC.md](SPEC.md); documento de origem: [PRD.md](PRD.md).

## Global Constraints

- `Automação.py` é o único arquivo de implementação do produto; `tests/test_automacao.py` conterá apenas testes e não será executado como parte da automação comercial.
- As entradas são `equipamentos_cadastrados.csv` e `novos_equipamentos.csv`, no diretório do projeto, com separador `;`, UTF-8 com BOM e cinco colunas: `id_equipamento`, `nome_equipamento`, `categoria`, `setor`, `situacao`.
- Preservar IDs como texto e a ordem das linhas de solicitações; não normalizar IDs silenciosamente.
- Nunca modificar, renomear, mover ou sobrescrever os dois CSVs; verificar seus hashes antes e depois.
- Classificar por comparação: ID já original tem precedência; primeira ocorrência de ID inédito é válida; seguintes são repetição interna.
- No lote atual, as contagens de referência são 342 originais, 259 solicitações, 35 já cadastrados, 24 repetidos internos, 200 novos válidos e 542 IDs finais. O código não deve fixar esses números.
- Manter `pyautogui.FAILSAFE` habilitado e exigir revisão da seleção e do lote piloto antes do lote completo.
- Reabrir e verificar o XLSX salvo; a aparência do Excel não prova conclusão.
- Não executar PyAutoGUI real nem assumir tela/mouse durante o desenvolvimento sem pedir autorização ao usuário no momento da operação. Testes com mocks não interagem com a tela.
- O diretório ainda não é um repositório Git; nenhuma tarefa presume commits ou worktrees.

## Review Focus

1. ID com zeros à esquerda: Task 1 e Task 2 testam preservação textual na leitura, classificação e saída.
2. Cabeçalho duplicado, coluna ausente ou ID vazio: Task 1 testa bloqueio antes da fase visual.
3. ID já cadastrado repetido na lista nova: Task 2 testa precedência de `ja_cadastrado` em todas as ocorrências.
4. Excel errado em foco ou linha inicial incerta: Task 5 testa interrupção antes da primeira digitação.
5. XLSX com contagem correta e atributo trocado: Task 4 testa reprovação por comparação dos cinco campos.

---

## Estrutura de arquivos planejada

| Caminho relativo ao projeto | Responsabilidade |
|---|---|
| `Automação.py` | Funções de leitura, validação, classificação, preparação, automação visual, verificação e `main()`. |
| `tests/test_automacao.py` | Testes isolados de dados e verificações com `tmp_path` e mocks; nenhum teste envia cliques reais. |
| `equipamentos_cadastrados.csv`, `novos_equipamentos.csv` | Entradas existentes, somente leitura. |
| `equipamentos_atualizados.xlsx` | Saída nominal prevista, em pasta e convenção ainda sujeitas à decisão D04. |

Os testes são um arquivo de verificação separado. O código operacional permanece apenas em `Automação.py`, conforme a SPEC.

## Decisões a resolver antes de suas tarefas dependentes

| Decisão da SPEC | Momento obrigatório | Resolução necessária |
|---|---|---|
| D01 | Antes da Task 5 | Confirmar Excel desktop, versões, escala e resolução para configurar interação visual. |
| D02 | Antes da Task 3 | Escolher se `status_cadastro` e `motivo_duplicidade` serão apenas exibidos ou também exportados em saída separada. |
| D03 | Antes da Task 5 | Definir mecanismo de confirmação do analista e tamanho do lote piloto. |
| D04 | Antes da Task 3 | Definir pasta da saída, identificação de execuções e política para XLSX existente. Nunca sobrescrever silenciosamente. |
| D05 | Antes da Task 6 | Definir como conservar e retomar uma saída parcial validada. |
| D06 | Antes da Task 1 | Definir política de espaços em IDs, outros campos vazios e situações não reconhecidas. Até lá, rejeitar entradas ambíguas antes do Excel. |
| D07 | Não bloqueia a implementação | Definir responsável, cronograma e meta de economia de tempo. |

## Task 1: Leitura segura e contrato de entrada (US01; RF01–RF02; M1)

**Files:** Modify `Automação.py`; create `tests/test_automacao.py`.

**Interfaces:** Produz `hash_arquivo(caminho: Path) -> str`, `carregar_csv(caminho: Path) -> pd.DataFrame`, `validar_base(df: pd.DataFrame, *, origem: str) -> None`, `carregar_bases(pasta: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]`. A leitura usa as cinco colunas por nome, `sep=";"`, `encoding="utf-8-sig"`, `dtype=str` e `keep_default_na=False`.

- [ ] **Step 1:** Registrar versões do ambiente e decidir D06; escrever testes `test_leitura_preserva_id_textual`, `test_cabecalho_ausente_ou_duplicado_bloqueia`, `test_id_vazio_e_original_duplicado_bloqueiam` e `test_entrada_ausente_nao_cria_saida` com CSVs temporários em `tmp_path`.
- [ ] **Step 2:** Executar `python -m pytest tests/test_automacao.py -q`; esperar falha por interfaces ainda ausentes. Não usar os CSVs comerciais como arquivos de teste modificáveis.
- [ ] **Step 3:** Implementar somente as interfaces desta tarefa. Confirmar arquivo e cabeçalhos antes de classificar; manter `hash_arquivo` sobre bytes originais.
- [ ] **Step 4:** Repetir o comando de testes; esperar aprovação dos quatro casos. Executar leitura read-only das bases reais e conferir 342/259 linhas, cinco colunas e hashes registrados.
- [ ] **Step 5:** Revisar diff de `Automação.py` e testes; registrar resultado do marco M1 antes de avançar.

## Task 2: Classificação e reconciliação (US01; RN01–RN04; RF03–RF05; M2)

**Files:** Modify `Automação.py`, `tests/test_automacao.py`.

**Interfaces:** Consome DataFrames da Task 1. Produz `classificar_solicitacoes(originais: pd.DataFrame, solicitacoes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]`: primeiro DataFrame com uma decisão por linha e colunas originais mais `status_cadastro`, `motivo_duplicidade`, `linha_origem`; segundo com apenas novos válidos em ordem, contendo as cinco colunas originais. Produz `resumir_classificacao(classificadas: pd.DataFrame) -> dict[str, int]`.

- [ ] **Step 1:** Escrever testes `test_existente_tem_precedencia`, `test_primeira_ocorrencia_nova_e_valida`, `test_ids_com_zeros_e_ordem`, `test_todas_as_linhas_conciliadas` usando DataFrames em memória.
- [ ] **Step 2:** Executar testes focados; esperar falha por interfaces ausentes.
- [ ] **Step 3:** Implementar classificação com conjunto de IDs originais e conjunto de novos já aceitos; aplicar a precedência da SPEC e verificar a soma das classes.
- [ ] **Step 4:** Executar testes focados; esperar aprovação. Rodar apenas a fase de classificação com os CSVs reais, sem PyAutoGUI; conferir 35, 24 e 200, IDs novos únicos e ausência de interseção com originais.
- [ ] **Step 5:** Apresentar resumo e amostra por classe ao usuário. A aprovação da seleção é o checkpoint antes de preparar inserção visual.

## Task 3: Cópia de trabalho e identidade da saída (US02; RF06; M3)

**Files:** Modify `Automação.py`, `tests/test_automacao.py`.

**Interfaces:** Consome `originais` da Task 1. Produz `preparar_copia(originais: pd.DataFrame, destino: Path) -> Path`, que cria um XLSX com cabeçalho e os cinco campos originais em ordem. A política para destino já existente é decidida em D04 antes do código.

- [ ] **Step 1:** Decidir D02 e D04; documentar as escolhas na configuração do programa sem acrescentar colunas ao cadastro principal por suposição.
- [ ] **Step 2:** Escrever `test_copia_contem_originais_e_ids_textuais` e `test_destino_existente_nao_e_sobrescrito_silenciosamente` com `tmp_path`.
- [ ] **Step 3:** Executar testes focados; esperar falha por interface ausente.
- [ ] **Step 4:** Implementar a cópia usando `openpyxl`, com destino fora dos CSVs e proteção contra sobrescrita.
- [ ] **Step 5:** Executar testes focados; esperar aprovação. Preparar e reabrir uma cópia de trabalho do lote real; conferir 342 linhas de dados e os cinco atributos, sem iniciar cliques.

## Task 4: Verificador independente do XLSX (US03; RF08; M5)

**Files:** Modify `Automação.py`, `tests/test_automacao.py`.

**Interfaces:** Consome `originais`, `novos_validos` e `destino` das Tasks 1–3. Produz `verificar_xlsx(destino: Path, originais: pd.DataFrame, novos_validos: pd.DataFrame) -> dict[str, int]`; lança erro explícito para ausência, duplicação, ordem ou atributo divergente. A comparação usa as cinco colunas e IDs como texto.

- [ ] **Step 1:** Escrever `test_xlsx_completo_e_aceito`, `test_contagem_correta_com_atributo_trocado_falha`, `test_id_duplicado_ou_faltante_falha` e `test_zeros_a_esquerda_preservados`, usando XLSX temporários.
- [ ] **Step 2:** Executar testes focados; esperar falha por verificador ausente.
- [ ] **Step 3:** Implementar reabertura com `openpyxl` e comparação linha a linha: originais primeiro, novos válidos depois, mesma ordem e mesmos cinco valores. Conferir unicidade e quantidade derivada das entradas.
- [ ] **Step 4:** Executar testes focados; esperar aprovação. Aplicar o verificador à cópia com 342 originais e zero novos como verificação intermediária.

## Task 5: Inserção assistida via Excel (US02; RF07; M4)

**Files:** Modify `Automação.py`, `tests/test_automacao.py`.

**Interfaces:** Consome `novos_validos`, `destino` e checkpoint aprovado. Produz `inserir_no_excel(novos_validos: pd.DataFrame, destino: Path, *, limite: int | None = None) -> int`, cujo retorno é a quantidade enviada e cuja execução exige Excel/janela/linha confirmados. `limite` serve ao lote piloto, sem mudar o conjunto de dados de origem.

- [ ] **Step 1:** Resolver D01 e D03; definir janela, linha inicial, método de confirmação e tamanho do lote piloto. Antes de qualquer execução real ou controle da tela/mouse pelo assistente, pedir autorização específica ao usuário.
- [ ] **Step 2:** Escrever testes com `unittest.mock` para `test_janela_errada_bloqueia`, `test_linha_inicial_invalida_bloqueia`, `test_so_novos_sao_enviados` e `test_failsafe_permanece_ativo`; nenhum teste envia clique real.
- [ ] **Step 3:** Executar testes focados; esperar falha por interface ausente.
- [ ] **Step 4:** Implementar interação visual sem desabilitar `FAILSAFE`, verificando foco e posição antes da digitação e interrompendo em caso de incerteza. Não inserir linhas bloqueadas.
- [ ] **Step 5:** Executar testes com mocks; esperar aprovação. Com autorização de controle da tela, executar apenas o lote piloto, salvar e verificar seus IDs antes do restante.
- [ ] **Step 6:** Após aprovação do piloto, inserir o restante, salvar e chamar `verificar_xlsx` da Task 4. Conferir 542 IDs únicos no lote atual.

## Task 6: Orquestração, falhas e retomada (US03; RN05–RN06; RF09; M6)

**Files:** Modify `Automação.py`, `tests/test_automacao.py`.

**Interfaces:** Consome funções das Tasks 1–5. Produz `main(pasta: Path | None = None) -> int` e `ids_pendentes_em_saida_parcial(destino: Path, novos_validos: pd.DataFrame) -> list[str]`. `main` retorna código de sucesso somente após verificação do XLSX e comparação dos hashes originais.

- [ ] **Step 1:** Resolver D05 e definir quais estados de saída parcial podem ser retomados; saída antiga não é prova da execução atual.
- [ ] **Step 2:** Escrever testes `test_saida_parcial_retorna_apenas_pendentes`, `test_hash_alterado_bloqueia_conclusao`, `test_falha_visual_nao_declara_sucesso` e `test_main_importavel_sem_abrir_excel`, com mocks para a interface.
- [ ] **Step 3:** Executar testes focados; esperar falha por interfaces ausentes.
- [ ] **Step 4:** Implementar orquestração com fases e mensagens de progresso, falha e destino. Na retomada, ler o XLSX parcial e comparar IDs/atributos antes de calcular pendentes; bloquear estados ambíguos.
- [ ] **Step 5:** Executar suíte `python -m pytest tests/test_automacao.py -q`; esperar aprovação. Verificar hashes dos CSVs originais.
- [ ] **Step 6:** Com autorização específica para controle de tela/mouse e aceite dos checkpoints, executar o fluxo real completo, reabrir a saída, conferir 342 + 200 = 542 e testar uma segunda execução sem reinserção. Registrar resultado e limitações; não declarar conclusão com falha de verificação.

## Critérios de entrega e auto-revisão do plano

- **Cobertura:** US01 em Tasks 1–2; US02 em Tasks 3 e 5; US03 em Tasks 4 e 6. RF01–RF09, RN01–RN06 e M1–M6 têm tarefa correspondente.
- **Dependências:** Task 2 usa dados da 1; Task 3 usa originais da 1 e seleção aprovada da 2; Task 4 usa a cópia da 3; Task 5 usa a verificação da 4; Task 6 integra todas.
- **Sem execução visual antecipada:** Tasks 1–4 podem ser desenvolvidas e verificadas sem assumir a tela. Tasks 5–6 têm um ponto explícito de autorização antes de controle real do mouse/teclado.
- **Próximo passo:** revisar este plano e resolver D06 antes da Task 1. As demais decisões são tomadas antes das tarefas dependentes, sem inventar aprovações.
