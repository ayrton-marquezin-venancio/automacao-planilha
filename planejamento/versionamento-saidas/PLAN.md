# Pastas de Saída por Versão Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking. Neste ambiente, as skills equivalentes estão em `C:\Users\giova\.agents\skills`. O usuário não autorizou commits nem worktrees.

**Goal:** Guardar cada execução do cadastro em `saidas/Planilha Versão N - AAAA-MM-DD`, com numeração sequencial e retomada segura.

**Architecture:** Duas funções locais em `Automação.py` interpretarão nomes de versões e reservarão uma pasta exclusiva. `main()` usará essa pasta para a cópia de trabalho e reconhecerá o mesmo padrão na retomada; a publicação existente continuará usando `destino.parent`.

**Tech Stack:** Python, `pathlib`, `datetime`, `re`, `pytest`, `openpyxl` já presentes no projeto.

**Spec:** `planejamento/versionamento-saidas/SPEC.md`

## Global Constraints

- Padrão exato: `Planilha Versão N - AAAA-MM-DD`; `N` começa em 1 e continua entre datas.
- Data da pasta: data local do computador; identificador UTC atual permanece no XLSX de trabalho.
- Todas as pastas e arquivos de execução ficam dentro de `saidas`; não sobrescrever nem apagar saídas.
- Uma versão reservada permanece consumida se a execução parar ou for recusada depois da criação da pasta.
- Retomada não aloca versão nova; aceita somente XLSX parcial em pasta válida diretamente sob `saidas`.
- Preservar CSVs, classificação, confirmações, PyAutoGUI, `time.sleep`, verificação e publicação comercial.
- Testes não abrem Excel nem controlam mouse/teclado. Não criar módulos Python, commits, push ou worktrees.

## Review Focus

1. `saidas` vazia ou ausente deve produzir Versão 1 — teste na Task 1.
2. Versões com lacunas e datas diferentes devem produzir `max(N)+1` — teste na Task 1.
3. Pastas com nome parecido, data impossível ou número `0` não devem afetar a contagem — teste na Task 1.
4. Colisão entre a leitura e a criação da pasta não deve sobrescrever a versão ocupada — teste na Task 1.
5. Retomada de caminho externo, aninhado ou com padrão antigo deve falhar sem criar outra pasta — teste na Task 2.

---

## File Structure

- `Automação.py`: modificar apenas imports padrão, funções auxiliares de versão e trechos de `main()` que montam/validam caminhos e exibem a pasta.
- `tests/test_automacao.py`: acrescentar testes da numeração e integração; atualizar caminhos e globs antigos `execucao_*` que verificam a estrutura de saída.
- Não modificar os CSVs ou criar outro módulo de aplicação.

### Task 1: Interpretar e reservar a próxima versão

**Files:**
- Modify: `Automação.py:3-10,18-20` (imports e funções auxiliares próximas às constantes)
- Test: `tests/test_automacao.py`

**Interfaces:**
- Consumes: `Path` e `date` da biblioteca padrão.
- Produces: `_extrair_numero_versao(nome: str) -> int | None` e `_reservar_pasta_versao(saidas: Path, data_execucao: date) -> Path`. A segunda cria e devolve a pasta reservada.

- [x] **Step 1: Escrever testes que falham para extração e sequência.** Adicionar `test_extrair_numero_versao_valida_nome_e_data` e `test_reservar_pasta_versao_sequencia_global`. Asserções: `"Planilha Versão 2 - 2026-11-03" -> 2`; nomes com versão 0, zeros à esquerda, data impossível ou formato antigo retornam `None`; diretório vazio retorna pasta `Planilha Versão 1 - 2026-11-03`; versões 1 e 3 com datas diferentes fazem a próxima ser 4.

  ```python
  assert automacao._extrair_numero_versao("Planilha Versão 2 - 2026-11-03") == 2
  assert automacao._extrair_numero_versao("Planilha Versão 0 - 2026-11-03") is None
  assert automacao._extrair_numero_versao("Planilha Versão 02 - 2026-11-03") is None
  assert automacao._extrair_numero_versao("Planilha Versão 2 - 2026-02-30") is None
  assert automacao._extrair_numero_versao("execucao_antiga") is None
  assert automacao._reservar_pasta_versao(tmp_path / "saidas", date(2026, 11, 3)).name == "Planilha Versão 1 - 2026-11-03"
  ```
- [x] **Step 2: Executar esses testes e confirmar falha pela ausência das funções.** Comando: `python -m pytest tests/test_automacao.py -q -k "extrair_numero_versao or reservar_pasta_versao"`. Esperado: FAIL por interfaces ainda inexistentes.
- [x] **Step 3: Implementar `_extrair_numero_versao` e `_reservar_pasta_versao` em `Automação.py`.** Usar correspondência integral do nome e `date.fromisoformat` para validar a data. Contar somente subdiretórios imediatos válidos. Criar `saidas` se ausente e reservar a próxima pasta com `mkdir(exist_ok=False)`; em `FileExistsError`, incrementar o número e tentar de novo. Outros erros de criação devem propagar.
- [x] **Step 4: Executar os testes da Task 1.** Mesmo comando do Step 2; esperado: PASS.
- [x] **Step 5: Testar colisão sem tocar saídas reais.** Adicionar `test_reservar_pasta_versao_colisao_nao_sobrescreve`, que simula a ocupação da versão escolhida entre a listagem e o `mkdir`; asserções: a pasta ocupada conserva seu arquivo e a função devolve a versão seguinte. Executar esse teste isolado; esperado: PASS.

### Task 2: Integrar o caminho novo e a retomada

**Files:**
- Modify: `Automação.py:612-635,640-642` (posições atuais; localizar por código antes da edição)
- Test: `tests/test_automacao.py`

**Interfaces:**
- Consumes: `_extrair_numero_versao(nome: str) -> int | None` e `_reservar_pasta_versao(saidas: Path, data_execucao: date) -> Path` da Task 1.
- Produces: `main(pasta: Path | None = None, *, parcial: Path | None = None) -> int` preservado, com novos caminhos de execução.

- [x] **Step 1: Escrever testes de integração que falham.** Adicionar `test_main_cria_versao_1_e_mostra_caminho`, `test_main_incrementa_versao_no_mesmo_dia`, `test_main_retomada_mantem_versao`, `test_main_rejeita_parcial_fora_da_pasta_de_versao` e `test_publicacao_final_permanece_na_pasta_da_versao`. Usar `tmp_path`, relógio local controlado e mocks das confirmações/GUI. Asserções: arquivos ficam sob `saidas/Planilha Versão N - AAAA-MM-DD`; segunda execução recebe `N+1`; a retomada mantém `N`; caminho externo, aninhado ou `execucao_*` é recusado antes de acessar Excel; o terminal mostra o caminho da pasta; cópia de trabalho e planilha final ficam na mesma pasta, com registros conferidos por `verificar_xlsx`. Nenhum teste chama Excel real.

  ```python
  assert (tmp_path / "saidas" / "Planilha Versão 1 - 2026-11-03").is_dir()
  assert (tmp_path / "saidas" / "Planilha Versão 2 - 2026-11-03").is_dir()
  assert destino_trabalho.parent == destino_final.parent
  assert destino_final.name == "equipamentos_atualizados.xlsx"
  assert destino_trabalho.parent.name in saida_terminal
  ```
- [x] **Step 2: Executar esses testes e confirmar falha pelo caminho antigo.** Comando: `python -m pytest tests/test_automacao.py -q -k "main_cria_versao_1 or main_incrementa_versao or main_retomada_mantem_versao or main_rejeita_parcial_fora or publicacao_final_permanece"`. Esperado: FAIL porque `main()` ainda usa `execucao_*`.
- [x] **Step 3: Alterar somente os caminhos em `main()`.** Obter `data_execucao` com `datetime.now().astimezone().date()`, reservar a pasta via Task 1 e manter o identificador UTC e o nome do XLSX de trabalho. Exibir o caminho da pasta junto da cópia de trabalho. Na retomada, exigir `destino.parent.parent == (pasta / "saidas").resolve()` e `_extrair_numero_versao(destino.parent.name) is not None`, preservando a validação do nome do XLSX e as verificações seguintes. Não alocar pasta quando `parcial` foi fornecido.
- [x] **Step 4: Executar os testes de integração da Task 2.** Mesmo comando do Step 2; esperado: PASS.
- [x] **Step 5: Atualizar testes existentes de caminhos de saída.** Trocar fixtures e globs `execucao_*` por nomes de versão válidos nos testes que dependem da estrutura antiga. Não alterar testes de classificação, comandos GUI ou regras de confirmação. Executar os testes de saída/retomada afetados; esperado: PASS, exceto falhas de linha de base documentadas antes da mudança.
- [x] **Step 6: Rodar a suíte existente e classificar eventuais falhas.** Comando: `python -m pytest tests/test_automacao.py -q`. Há registro anterior de expectativas antigas para a quebra de linha da primeira confirmação; registrar esse desvio separadamente se persistir, sem mudar a confirmação para fazer a suíte passar.
- [x] **Step 7: Conferir arquivos e diff.** Confirmar que apenas `Automação.py` e `tests/test_automacao.py` foram alterados na implementação, que os hashes dos dois CSVs originais continuam iguais e que nenhum teste abriu Excel real. Revisar a criação exclusiva da pasta, a retomada, os nomes e o destino da planilha final.

## Execution Handoff

Este documento é somente o plano. A implementação deve seguir as tarefas na ordem, com verificação após cada uma. Não fazer commits, push, worktrees ou limpeza de `saidas`.
