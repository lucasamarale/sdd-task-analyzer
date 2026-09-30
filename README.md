# sdd-task-analyzer

TaskAnalyzer, um módulo de métricas de produtividade construído com **Spec-Driven Development**: a especificação vem primeiro, o código é gerado por assistente de IA a partir dela, e um Test Harness em pytest decide se o resultado é aceito.

Projeto do Bootcamp III, Ciência da Computação, CEUB. Autor: **Lucas Amaral Evangelista**, RA 22508120.

## Status

| Fase | Entrega | Situação |
|---|---|---|
| 1 | Especificação SDD, cenários de aceite e CONTEXT_RULES | concluída |
| 2 | Repositório, código gerado via IA, Test Harness e Pull Requests | **concluída: 25 testes, 100% aprovados** |
| 3 | GitHub Actions, Docker e relatório de governança | próxima etapa |

**Build:** `pytest -v` com 25 de 25 testes aprovados, em Python 3.12. A execução automática no GitHub Actions, com badge de status, entra na Fase 3.

## O que o módulo faz

Recebe uma lista de tarefas e devolve:

| Campo | O que é |
|---|---|
| `total_tarefas` | quantidade de tarefas recebidas |
| `total_concluidas` | quantas têm status `concluida` |
| `total_pendentes` | quantas têm status `pendente` |
| `tempo_medio_conclusao_horas` | média de horas entre criação e conclusão |
| `tempo_medio_por_prioridade_horas` | a mesma média, para `alta`, `media` e `baixa` |
| `taxa_atraso_percentual` | percentual das concluídas depois do prazo |

Sem tarefa concluída, médias e taxa valem `0.0`, sem exceção. Entrada inválida levanta `TaskValidationError`, citando a tarefa e o campo.

```python
from datetime import UTC, datetime, timedelta
from src.task_analyzer import Tarefa, analyze_tasks

criada = datetime(2026, 9, 1, 8, 0, tzinfo=UTC)
tarefas = [
    Tarefa(1, criada, criada + timedelta(hours=3), "alta", "concluida",
           data_conclusao=criada + timedelta(hours=2)),
    Tarefa(2, criada, criada + timedelta(hours=8), "media", "pendente"),
]
analyze_tasks(tarefas)
# {'total_tarefas': 2, 'total_concluidas': 1, 'total_pendentes': 1,
#  'tempo_medio_conclusao_horas': 2.0,
#  'tempo_medio_por_prioridade_horas': {'alta': 2.0, 'media': 0.0, 'baixa': 0.0},
#  'taxa_atraso_percentual': 0.0}
```

## Como executar

Requer **Python 3.11 ou superior**.

```bash
git clone https://github.com/lucasamarale/sdd-task-analyzer.git
cd sdd-task-analyzer
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

## Estrutura

```text
sdd-task-analyzer/
├── README.md                     # este arquivo
├── CONTEXT_RULES.md              # regras de governança da IA
├── .gitignore
├── requirements.txt              # única dependência: pytest
├── pyproject.toml                # configuração do pytest
├── specs/
│   └── task_analyzer_spec.md     # o contrato, versão 1.1
├── tests/
│   └── test_harness.py           # Test Harness: 25 testes
└── src/
    └── task_analyzer.py          # código gerado via IA e homologado
```

## Como o código foi feito

1. **Contrato primeiro.** [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md) define entradas, saídas, regras de negócio e cenários de aceite. A versão 1.1 alinhou o contrato ao enunciado da Fase 2, com cada mudança registrada na seção 0.
2. **Regras para a IA.** [`CONTEXT_RULES.md`](CONTEXT_RULES.md) diz o que o assistente deve e não deve fazer.
3. **Testes antes do código.** O Test Harness foi escrito a partir dos cenários de aceite e entrou na `main` antes da implementação.
4. **Código gerado por IA.** O assistente recebeu a especificação e as regras, reformulou o contrato com as próprias palavras e gerou `src/task_analyzer.py`.
5. **Homologação humana.** A primeira versão passou em todos os testes, mas violava duas CONTEXT_RULES: duas linhas acima de 100 colunas e um `assert` usado no lugar de verificação explícita. Foi corrigida antes do merge.

Cada etapa entrou na `main` por Pull Request: [#1 especificação](../../pull/1), [#2 Test Harness](../../pull/2) e [#3 implementação](../../pull/3).
