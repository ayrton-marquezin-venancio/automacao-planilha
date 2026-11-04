# Pastas de saída por versão — especificação

## Objetivo

Cada nova execução do cadastro de equipamentos deve guardar sua cópia de trabalho e sua planilha final em uma pasta própria dentro de `saidas`.

## Nome e numeração

- Padrão exato da pasta: `Planilha Versão N - AAAA-MM-DD`, com `N` inteiro positivo sem zeros à esquerda e data local do computador.
- A numeração é global e não reinicia quando a data muda.
- Se não existir pasta válida no novo padrão, a próxima versão é 1. As execuções antigas de rascunho foram apagadas pelo usuário.
- Havendo versões válidas, usar o maior `N` mais 1, inclusive quando houver lacunas ou versões parciais.
- Pastas com outros nomes, arquivos soltos e nomes com data inválida não participam da contagem e não são alterados.
- Reservar a pasta sem sobrescrita. Se outro processo ocupar o número escolhido, tentar o próximo.
- Toda tentativa que chegou à criação da pasta consome uma versão, mesmo que seja interrompida.

## Arquivos e retomada

- Manter o identificador UTC existente no nome do XLSX de trabalho: `equipamentos_atualizados_<identificador>.xlsx`.
- Manter a planilha final `equipamentos_atualizados.xlsx` na mesma pasta da versão.
- O caminho completo da pasta e da planilha final deve aparecer no terminal.
- A retomada aceita somente um XLSX parcial diretamente em uma pasta de versão válida dentro de `saidas`, preservando as demais verificações de integridade.
- Retomar uma versão não cria outra pasta ou outro número.
- Não renomear, mover, excluir ou sobrescrever saídas existentes; não alterar os CSVs originais.

## Limites

Manter a classificação dos equipamentos, as confirmações, os comandos PyAutoGUI, os intervalos `time.sleep`, a conferência do XLSX e a publicação final existentes. Não abrir Excel nos testes; usar diretórios temporários e mocks. Não criar módulos Python adicionais nem fazer commits ou push.
