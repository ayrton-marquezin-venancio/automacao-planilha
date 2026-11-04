# Planejamento — Cadastro de Equipamentos

Este índice reúne os **16 documentos preexistentes** do projeto, reorganizados em 04/11/2026. Os conteúdos históricos foram preservados; somente caminhos e links necessários à movimentação foram ajustados.

Para entender o funcionamento atual, comece pelo [README do projeto](../README.md) e pelo [código](../Automa%C3%A7%C3%A3o.py). Os planos registram intenções e decisões de cada momento: não execute automaticamente tarefas antigas como se ainda estivessem pendentes.

## Ordem recomendada de leitura

| Ordem | Documentos | Finalidade e contexto |
|---|---|---|
| 1 | [PRD](projeto/PRD.md) e [SPEC geral](projeto/SPEC.md) | Problema empresarial, contrato dos CSVs, regras e desenho inicial de 30/10/2026. As descrições de implementação não iniciada são históricas. |
| 2 | [Plano inicial](projeto/2026-10-30-plano-inicial.md) e [plano com atualização do piloto](projeto/PLAN.md) | Tarefas de construção do fluxo. São documentos distintos, preservados sem sobrescrita. |
| 3 | [Relatório de andamento e auditoria](projeto/RELATORIO_STATUS_PROJETO.md) | Registra o piloto e um aditivo posterior sobre a carga completa. Leia também o aditivo, não apenas o resumo inicial. |
| 4 | [Confirmação inicial: especificação](confirmacao-terminal/spec.md), [plano](confirmacao-terminal/plan.md) e [tarefas](confirmacao-terminal/tasks.md) | Interpretação de SIM/NÃO e entradas inválidas; registros de testes e revisão daquele escopo. |
| 5 | [Piloto e continuação: especificação](autorizacoes-piloto-continuacao/spec.md), [plano](autorizacoes-piloto-continuacao/plan.md) e [tarefas](autorizacoes-piloto-continuacao/tasks.md) | Autorizações adicionais e retorno ao terminal; inclui ensaio visual interrompido. |
| 6 | [Pastas de versões: especificação](versionamento-saidas/SPEC.md), [plano](versionamento-saidas/PLAN.md) e [registro de execução](versionamento-saidas/REGISTRO_EXECUCAO.md) | Numeração, data, reserva concorrente e condições de retomada. |
| 7 | [Ordenação: especificação](ordenacao-equipamentos/SPEC.md) e [plano](ordenacao-equipamentos/PLAN.md) | Publicação ordenada sem alterar a cópia de trabalho e suas regras de retomada. |

## Como interpretar os registros

- **PRD/SPEC iniciais:** dizem que o script ainda tinha somente imports. Isso descreve a data de elaboração; o código atual já contém o fluxo operacional.
- **Planos iniciais:** o plano com atualização do piloto ainda contém a frase “nenhuma tarefa foi executada” e tarefas desmarcadas. Não houve marcação retroativa nesta organização.
- **Relatório de andamento:** o primeiro resumo descreve somente o piloto; o aditivo posterior registra 542 equipamentos conferidos. Esses fatos pertencem às execuções ali identificadas.
- **Ordenação:** o plano mantém tarefas desmarcadas, mas o código atual contém `_publicar_final_ordenado` e suas chamadas nos dois caminhos de conclusão. A presença do código não substitui evidências de execução e aceite.
- **Testes:** os registros de 28, 69, 153 testes e os resultados do registro de versionamento são históricos e têm escopos diferentes. Não devem ser combinados ou apresentados como resultado de uma nova execução.
- **Foco do terminal:** T06 das autorizações registra interrupção intencional por fail-safe e não comprova integralmente a terceira confirmação no ensaio. Essa pendência documental foi preservada.
- **Publicação:** a SPEC inicial prevê originais seguidos de novos na saída. A especificação posterior de ordenação diferencia o final ordenado da cópia de trabalho, que conserva a ordem de inserção.
- **Git:** afirmações de que o projeto ainda não tinha repositório descrevem a época do documento. Atualmente existe histórico Git; a tag `v1.0.0` foi preservada nesta organização.
- **Referências locais:** caminhos de execuções antigas são evidências históricas e podem não existir mais. Números de linhas do código também correspondem à versão inspecionada na ocasião.
- **Testes locais:** menções a `tests/test_automacao.py` e comandos pytest foram preservadas como parte dos planos. A pasta foi retirada do rastreamento atual, mantida localmente e não acompanha um novo clone. Isso não apaga sua presença nos commits anteriores.

Caminhos do produto escritos sem prefixo relativo, como `Automação.py`, `tests/` e `saidas/`, referem-se à raiz do projeto. Links Markdown são relativos ao documento.

## Mapa dos caminhos antigos para os novos

Os caminhos da primeira coluna são somente referências históricas; os links da segunda coluna apontam para os documentos atuais.

| Caminho anterior, relativo à raiz | Documento atual, dentro de planejamento/ |
|---|---|
| `Elaboração IA/PRD.md` | [projeto/PRD.md](projeto/PRD.md) |
| `Elaboração IA/SPEC.md` | [projeto/SPEC.md](projeto/SPEC.md) |
| `Elaboração IA/PLAN.md` | [projeto/PLAN.md](projeto/PLAN.md) |
| `Elaboração IA/RELATORIO_STATUS_PROJETO.md` | [projeto/RELATORIO_STATUS_PROJETO.md](projeto/RELATORIO_STATUS_PROJETO.md) |
| `docs/superpowers/plans/2026-10-30-cadastro-equipamentos.md` | [projeto/2026-10-30-plano-inicial.md](projeto/2026-10-30-plano-inicial.md) |
| `PLAN.md` | [ordenacao-equipamentos/PLAN.md](ordenacao-equipamentos/PLAN.md) |
| `docs/superpowers/plans/2026-11-03-ordenacao-equipamentos-por-id-spec.md` | [ordenacao-equipamentos/SPEC.md](ordenacao-equipamentos/SPEC.md) |
| `docs/superpowers/plans/2026-11-03-pastas-de-saida-por-versao.md` | [versionamento-saidas/PLAN.md](versionamento-saidas/PLAN.md) |
| `docs/superpowers/plans/2026-11-03-pastas-de-saida-por-versao-spec.md` | [versionamento-saidas/SPEC.md](versionamento-saidas/SPEC.md) |
| `docs/superpowers/plans/2026-11-03-pastas-de-saida-por-versao-progress.md` | [versionamento-saidas/REGISTRO_EXECUCAO.md](versionamento-saidas/REGISTRO_EXECUCAO.md) |
| `specs/confirmacao-terminal/spec.md` | [confirmacao-terminal/spec.md](confirmacao-terminal/spec.md) |
| `specs/confirmacao-terminal/plan.md` | [confirmacao-terminal/plan.md](confirmacao-terminal/plan.md) |
| `specs/confirmacao-terminal/tasks.md` | [confirmacao-terminal/tasks.md](confirmacao-terminal/tasks.md) |
| `specs/autorizacoes-piloto-continuacao/spec.md` | [autorizacoes-piloto-continuacao/spec.md](autorizacoes-piloto-continuacao/spec.md) |
| `specs/autorizacoes-piloto-continuacao/plan.md` | [autorizacoes-piloto-continuacao/plan.md](autorizacoes-piloto-continuacao/plan.md) |
| `specs/autorizacoes-piloto-continuacao/tasks.md` | [autorizacoes-piloto-continuacao/tasks.md](autorizacoes-piloto-continuacao/tasks.md) |

## Verificação desta reorganização

O escopo desta entrega é documental: centralização, índice, README técnico e exclusão de `tests/` apenas do rastreamento Git.

A conferência compara os 16 arquivos com a revisão anterior, permitindo somente as substituições explícitas de caminhos e links. Código, CSVs, testes locais e saídas existentes devem manter seus hashes. As validações desta entrega não substituem testes funcionais nem um ensaio no Excel.

## Conservação e limpeza

| Pasta | Orientação |
|---|---|
| `planejamento/` | Preservar: concentra requisitos, decisões, planos e evidências históricas. |
| `docs/`, `specs/`, `Elaboração IA/` | As pastas antigas só foram removidas depois da movimentação de todos os seus documentos e da confirmação de que estavam vazias. |
| `tests/` | Preservar localmente para regressões futuras; ignorada pelo Git nesta revisão. |
| `__pycache__/`, `.pytest_cache/` | Caches regeneráveis; podem ser removidos quando não estiverem em uso. Não foram apagados nesta entrega. |
| `saidas/` | Preservar execuções necessárias para histórico e retomada. Excluir pastas pode afetar a próxima numeração. Não foi limpa nesta entrega. |
| `.git/` | Preservar: contém o histórico e a configuração do repositório local. |
