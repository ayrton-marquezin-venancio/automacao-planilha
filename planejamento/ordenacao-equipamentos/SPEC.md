# Ordenação dos equipamentos por ID — especificação

## Objetivo

Publicar `equipamentos_atualizados.xlsx` com todos os equipamentos em ordem crescente de `id_equipamento`, sem alterar os CSVs ou a ordem da cópia de trabalho usada pelo PyAutoGUI e pela retomada.

## Dados e ordenação

- Os dois CSVs atuais contêm IDs textuais no padrão `EQP` seguido de quatro dígitos. A ordenação textual crescente desse padrão equivale à ordem numérica do sufixo.
- Preservar cada ID literalmente, inclusive zeros à esquerda, e manter juntos todos os atributos da mesma linha.
- Se aparecer um ID fora desse padrão, não publicar uma ordem presumida: interromper a publicação com erro claro, deixando a cópia de trabalho intacta para decisão sobre a regra de negócio.
- Não modificar a classificação de duplicidades nem a sequência de inserção no Excel.

## Publicação e integridade

- Conferir primeiro o XLSX de trabalho na ordem atual: originais seguidos de novos válidos.
- Após conferir os hashes dos CSVs, criar o XLSX final na mesma pasta de versão, com as linhas ordenadas e IDs formatados como texto. Reabrir o arquivo e comparar cabeçalho, quantidade, IDs e todos os atributos com a tabela ordenada esperada.
- A ordenação muda os bytes e a sequência das linhas; portanto, não exigir igualdade de SHA-256 entre XLSX de trabalho e final. A verificação de SHA-256 dos CSVs permanece obrigatória.
- Aplicar a publicação aos dois caminhos de conclusão: fluxo normal e retomada já completa, inclusive quando não há novos equipamentos.
- Nunca sobrescrever um XLSX final existente. Na retomada, aceitar um final preexistente somente se ele já corresponder integralmente à versão ordenada esperada; caso contrário, interromper com mensagem de incompatibilidade e preservá-lo.
- Não declarar conclusão se a criação ou a verificação do final falhar. Não apagar automaticamente um arquivo parcial ou incompatível.

## Verificação

Usar somente arquivos temporários e simulações das interações gráficas. Cobrir ordem, IDs textuais, zeros à esquerda, atributos, ausência de duplicações, os dois fluxos de conclusão, retomada idempotente, final antigo fora de ordem e falhas de integridade. Não abrir o Excel nem executar PyAutoGUI real nos testes.

## Limites

Alterar apenas `Automação.py` e `tests/test_automacao.py` durante a implementação. Preservar as confirmações, intervalos, comandos gráficos, classificação e arquivos comerciais existentes. Não fazer commits ou push sem autorização.
