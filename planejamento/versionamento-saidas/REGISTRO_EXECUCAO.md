# SDD ledger — plan: planejamento/versionamento-saidas/PLAN.md

- Ruling: O projeto não é um repositório Git e o plano proíbe commits e worktrees — acompanhar as tarefas neste arquivo e preservar saídas reais — custo: sem histórico Git desta alteração.
- Ruling: A skill `test-driven-development` não está instalada — executar ciclos RED→GREEN explicitamente com pytest — custo: sem instruções auxiliares dessa skill.
- Pre-flight: Task 1 produz `_extrair_numero_versao` e `_reservar_pasta_versao`; Task 2 consome exatamente essas assinaturas.
- Baseline SHA-256: `Automação.py` 584CD3103676FFE204BF94C3AE15DF5EC1092D248269B88B426559860BB36C4A; `tests/test_automacao.py` 659D1722D94D21A13B06856F8B3BA38C4168479632A7E3B3810D2ABF014A9BAB.
- CSV SHA-256: `equipamentos_cadastrados.csv` 9E2E6D1FFC2743C79BF0EC4ACCAA37EA70E9AB4C3863FFE573BA11C7BAA807E1; `novos_equipamentos.csv` 16F0750759F07364BB33A207711CEDB9599041F022D05829B1CED99B8652FD5E.
- Baseline: `python -m pytest tests/test_automacao.py -q --tb=no` → 79 passed, 74 failed antes das alterações; expectativas antigas da primeira pergunta e do hash da função. Ruling: não ajustar a confirmação aprovada para satisfazer testes antigos — fora do escopo — custo: suíte completa permanece vermelha até revisão separada dos testes.
- Task 1: RED `-k "extrair_numero_versao or reservar_pasta_versao"` → 2 AttributeError; GREEN → 3 passed, 153 deselected. Interfaces entregues; colisão preservou conteúdo da pasta ocupada.
- Task 1: complete (sem commits por restrição do usuário; tests: `python -m pytest tests/test_automacao.py -q -k "extrair_numero_versao or reservar_pasta_versao"` → 3 passed).
- Task 2: RED dos testes de integração → 4 failed, 3 passed pelo caminho antigo; GREEN → 7 passed. Testes antigos de caminhos atualizados; seleção de testes de versão, saída e retomada → 13 passed antes da revisão.
- Final review: revisor independente, somente leitura. Important: dois processos em datas diferentes poderiam usar o mesmo número global; Minor: relógio real tornava os testes de data frágeis.
- Final: fixed numeração concorrente — `test_reservar_versoes_concorrentes_em_datas_diferentes` RED (`{1}`), GREEN (`{1,2}`), seleção final 14 passed. Ruling: usar mutex nomeado local do Windows para serializar leitura e reserva sem arquivo solto em `saidas` — adequado ao aplicativo desktop Windows — custo se errado: processos em sessões Windows diferentes não compartilham o mutex local.
- Final: relógio controlado aplicado aos testes de `main`; data local 2026-11-03 e identificador UTC 20261104T010203 verificados. Ruling: cumprir o relógio fixo exigido pela Task 2 apesar de classificado Minor na revisão — custo: nenhum arquivo comercial alterado; testes um pouco mais extensos.
- Task 2: complete (sem commits; testes focados 14 passed, 150 deselected). Suíte completa final: 90 passed, 74 failed; as 74 falhas já existiam na linha de base e envolvem a primeira confirmação.
- Integridade: hashes SHA-256 dos dois CSVs idênticos à linha de base; `rg --files saidas` não encontrou arquivos. Excel real e PyAutoGUI não foram executados.
