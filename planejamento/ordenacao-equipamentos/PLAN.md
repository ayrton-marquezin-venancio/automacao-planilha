# Ordenação dos equipamentos por ID — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` or `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar a planilha final com os equipamentos em ordem crescente de ID, preservando a cópia de trabalho e comprovando a integridade dos registros.

**Architecture:** A inserção pelo PyAutoGUI e a retomada continuam na ordem de entrada. Uma função de publicação confere a cópia completa, ordena os registros em memória, cria um novo XLSX final e reabre esse arquivo para validação. Os dois caminhos de conclusão de `main` usam a mesma função.

**Tech Stack:** Python, pandas, openpyxl, pathlib e pytest; sem nova dependência.

**Spec:** `planejamento/ordenacao-equipamentos/SPEC.md`

## Global Constraints

- Arquivos de implementação: `Automação.py` e `tests/test_automacao.py`; não criar outro módulo Python.
- Os CSVs originais, as planilhas existentes em `saidas` e o XLSX de trabalho não podem ser alterados pela ordenação.
- O XLSX final continua em `saidas/Planilha Versão N - AAAA-MM-DD/equipamentos_atualizados.xlsx`.
- Os IDs permanecem texto com zeros à esquerda. Os dados atuais usam `EQP` mais quatro dígitos; fora desse padrão, bloquear a publicação e solicitar regra de negócio.
- A classificação, as confirmações, os tempos de espera e os comandos PyAutoGUI permanecem intactos.
- Continuar verificando SHA-256 dos dois CSVs; substituir somente a comparação de bytes entre o XLSX de trabalho e o final por conferência semântica das linhas.
- Não sobrescrever, apagar, mover ou migrar automaticamente um final preexistente. Testes não abrem Excel nem controlam mouse ou teclado.
- Não executar a automação real, criar worktree, commit ou push sem autorização.

## Review Focus

1. ID `EQP0010` junto de `EQP0002`: ordem crescente correta e zeros preservados; teste da Tarefa 1.
2. ID inesperado, como `EQP10`, ou duplicado: publicação bloqueada antes de declarar sucesso; teste da Tarefa 1.
3. Linha com mesmo ID e atributo alterado: validação do final rejeita a divergência; teste da Tarefa 1.
4. Retomada com final antigo fora de ordem: erro explícito, sem sobrescrever; teste da Tarefa 1 e integração da Tarefa 2.
5. Cópia parcial com três itens e continuação posterior: ordem de inserção e cálculo dos pendentes preservados; teste da Tarefa 2.

---

## Mapa de arquivos e decisões

- `Automação.py:232-313`: reutilizar `preparar_copia` e `verificar_xlsx`; adicionar a função de publicação após a verificação do XLSX. Não mudar a regra de leitura e validação dos CSVs.
- `Automação.py:728-742` e `Automação.py:800-812`: substituir os dois blocos de cópia e igualdade de hash do XLSX pela mesma função; manter `conferir_hashes(pasta, hashes)` antes de publicar.
- `tests/test_automacao.py`: acrescentar testes específicos e atualizar somente as expectativas que pressupõem igualdade de bytes, ordem antiga ou chamadas a `shutil.copyfile`.
- `planejamento/ordenacao-equipamentos/SPEC.md`: contrato da funcionalidade. Este `PLAN.md` é o roteiro de implementação.

### Task 1: Publicação ordenada e validação do XLSX final

**Files:**
- Modify: `Automação.py:274-314` (inserir função após `verificar_xlsx`)
- Test: `tests/test_automacao.py` (testes da publicação)

**Interfaces:**
- Consumes: `preparar_copia(originais: pd.DataFrame, destino: Path, *, capacidade: int = 0) -> Path` e `verificar_xlsx(destino: Path, originais: pd.DataFrame, novos_validos: pd.DataFrame) -> dict[str, int]`.
- Produces: `_publicar_final_ordenado(destino: Path, originais: pd.DataFrame, novos_validos: pd.DataFrame, final: Path, *, permitir_existente: bool = False) -> dict[str, int]`. O retorno mantém as contagens da cópia de trabalho (`originais`, `novos`, `total`); `permitir_existente=True` significa apenas verificar o final existente, nunca sobrescrevê-lo.

- [ ] **Step 1: Escrever testes que falhem.** Criar `test_publicacao_ordena_final_sem_alterar_trabalho`: montar em `tmp_path` uma cópia completa com IDs `EQP0010`, `EQP0002`, `EQP0001`, atributos distintos; chamar `_publicar_final_ordenado`; exigir IDs finais `EQP0001`, `EQP0002`, `EQP0010`, cada linha com seus atributos originais, IDs do XLSX como `str`, formato `@` na coluna de ID, bytes da cópia de trabalho inalterados e contagens corretas. Criar `test_publicacao_rejeita_id_fora_do_padrao_e_duplicado`, exigindo ausência de novo final após falha. Criar `test_publicacao_rejeita_final_alterado` com um atributo adulterado.
- [ ] **Step 2: Confirmar RED.** Executar `python -m pytest tests/test_automacao.py -k "publicacao_ordena_final or publicacao_rejeita" -q`. Esperado: falha por ausência de `_publicar_final_ordenado`; nenhum teste deve abrir Excel.
- [ ] **Step 3: Implementar a função mínima.** Conferir `destino` com `verificar_xlsx` antes de criar o final; concatenar `originais` e `novos_validos` nas colunas de `COLUNAS`; exigir para todos os IDs o padrão `^EQP[0-9]{4}$`; ordenar por `id_equipamento` em ordem crescente e estável, sem converter IDs. Se `final` não existir, usar `preparar_copia(tabela_ordenada, final)`; se existir e `permitir_existente=False`, lançar `FileExistsError`; se existir e `permitir_existente=True`, apenas verificar. Reabrir e conferir o final com `verificar_xlsx(final, tabela_ordenada, tabela_ordenada.iloc[0:0])`. Em caso de final existente divergente, emitir erro que identifique o arquivo e preserve seus bytes. Retornar as contagens da cópia de trabalho.
- [ ] **Step 4: Confirmar GREEN e casos de retomada.** Repetir o comando do Step 2. Acrescentar `test_publicacao_final_existente_ordenado_e_idempotente`: segunda chamada com `permitir_existente=True` aceita o final correto sem mudar bytes ou data de modificação; `test_publicacao_final_antigo_desordenado_e_preservado`: exige erro claro e hash idêntico do final preexistente. Executar esses testes e revisar o diff da tarefa.

### Task 2: Integrar os dois caminhos de conclusão sem falsa comparação por hash

**Files:**
- Modify: `Automação.py:728-742`, `Automação.py:800-812` e import de `shutil` se ficar sem uso
- Test: `tests/test_automacao.py:158-201`, `:528-562`, `:615-752`, `:945-1020`

**Interfaces:**
- Consumes: `_publicar_final_ordenado(...) -> dict[str, int]` da Tarefa 1; `conferir_hashes(pasta: Path, hashes: dict[str, str]) -> None` permanece antes da publicação.
- Produces: o mesmo `main(pasta: Path | None = None, *, parcial: Path | None = None) -> int`, agora com XLSX final ordenado em ambos os fluxos.

- [ ] **Step 1: Escrever testes de integração que falhem.** Criar `test_ordenacao_main_fluxo_normal` com IDs de entrada fora de ordem: exigir final ordenado, trabalho na ordem de inserção e ausência de linhas perdidas ou duplicadas. Criar `test_retomada_final_ordenado` para final ausente e outro já ordenado; criar `test_retomada_final_antigo_preservado` para final fora de ordem; criar `test_ordenacao_main_sem_novos` com `len(novos) == 0`; criar `test_piloto_ordem_preservada` para confirmar que `ids_pendentes_em_saida_parcial` e a sequência enviada ao PyAutoGUI simulado não mudaram. Os mocks devem proibir GUI real.
- [ ] **Step 2: Confirmar RED.** Executar `python -m pytest tests/test_automacao.py -k "ordenacao_main or retomada_final_ordenado or piloto_ordem_preservada" -q`. Esperado: pelo menos um teste falha com o código de publicação atual.
- [ ] **Step 3: Alterar somente os dois pontos de publicação.** No ramo `feitos == len(novos)`, chamar `_publicar_final_ordenado(..., permitir_existente=True)` após `conferir_hashes`; no ramo normal, chamar `_publicar_final_ordenado(...)` após `conferir_hashes` e usar seu retorno para o resumo. Remover a comparação `hash_arquivo(final) != hash_arquivo(destino)` nos dois ramos, pois a ordenação muda os bytes. Não remover a verificação dos hashes dos CSVs. Remover `shutil` apenas se não houver outra utilização.
- [ ] **Step 4: Atualizar testes dependentes do mecanismo antigo.** Em `fluxo_autorizacoes`, observar a nova função de publicação em vez de `shutil.copyfile`; atualizar asserções que supõem ordem antiga do final. Ajustar o teste de recusa inicial para falhar se a nova função publicar sem confirmação. Manter as asserções sobre a cópia parcial, a autorização e o número de lotes.
- [ ] **Step 5: Confirmar GREEN.** Executar `python -m pytest tests/test_automacao.py -k "ordenacao_main or retomada_final or piloto_ordem_preservada or publicacao or continuacao or main_sem_novos" -q`. Esperado: testes do escopo aprovados; nenhum arquivo de `saidas` real tocado. Inspecionar o diff para confirmar que somente publicação e expectativas dependentes mudaram.

### Task 3: Regressão completa e decisão sobre falhas preexistentes

**Files:**
- Test: `tests/test_automacao.py`
- Review: `Automação.py`, `tests/test_automacao.py`

**Interfaces:** Nenhuma nova interface; entrega a evidência de que a ordenação não alterou classificação, confirmações, retomada e publicação.

- [ ] **Step 1: Executar verificação estática.** Rodar `python -c "import ast, pathlib; ast.parse(pathlib.Path('Automação.py').read_text(encoding='utf-8'))"`. Esperado: saída vazia e código zero.
- [ ] **Step 2: Executar a suíte completa sem GUI real.** Rodar `python -m pytest tests/test_automacao.py -q`. Registrar total aprovado/falho e comparar falhas com a linha de base atual. Investigar cada falha nova; corrigir apenas regressões desta mudança.
- [ ] **Step 3: Tratar expectativas antigas com critério.** Se testes ainda pressupuserem o texto anterior da primeira confirmação ou um hash fixo dessa função, conferir a implementação aprovada e atualizar somente as expectativas comprovadamente obsoletas, sem alterar a confirmação. Reexecutar os testes afetados; não mudar testes para esconder falhas reais.
- [ ] **Step 4: Revisão final.** Conferir especialmente: nenhum ID convertido para número; nenhum CSV ou XLSX existente alterado; ordem de trabalho preservada; ambos os ramos de `main` cobertos; final existente divergente bloqueado; `conferir_hashes` mantido; nenhuma declaração de sucesso antes de reabrir o final. Registrar falhas residuais caso a suíte não fique verde. Não executar a automação gráfica.

## Critérios de conclusão

- A planilha final nova apresenta todos os equipamentos em ordem crescente de ID, com zeros, atributos e contagens preservados.
- A cópia de trabalho mantém a ordem necessária ao piloto e à retomada.
- Final existente correto é aceito sem escrita; final divergente é rejeitado sem sobrescrita.
- Ambos os caminhos de conclusão usam a mesma validação sem exigir hashes iguais para XLSX de ordens diferentes.
- Testes relevantes e revisão final têm resultados registrados; nenhuma falha remanescente é ocultada.
