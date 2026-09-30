"""Test Harness do TaskAnalyzer.

Cada teste traduz um cenário de aceite da seção 2 de specs/task_analyzer_spec.md.
O nome do teste diz o cenário e o comportamento verificado.

Execução: pytest -v
"""

import copy
from datetime import UTC, datetime, timedelta

import pytest

from src.task_analyzer import Tarefa, TaskValidationError, analyze_tasks

INICIO = datetime(2026, 9, 1, 8, 0, tzinfo=UTC)


def tarefa(
    id_tarefa: int,
    prioridade: str,
    status: str,
    horas_ate_concluir: float | None = None,
    horas_de_prazo: float = 24,
) -> Tarefa:
    """Monta uma tarefa criada em INICIO, com prazo e conclusão relativos a ela."""
    conclusao = (
        INICIO + timedelta(hours=horas_ate_concluir) if horas_ate_concluir is not None else None
    )
    return Tarefa(
        id_tarefa=id_tarefa,
        data_criacao=INICIO,
        prazo=INICIO + timedelta(hours=horas_de_prazo),
        prioridade=prioridade,
        status=status,
        data_conclusao=conclusao,
    )


# ------------------------------------------------------------------ Cenário 1, sucesso


@pytest.fixture
def cenario_1() -> list[Tarefa]:
    """Seis tarefas: quatro concluídas (duas atrasadas), uma pendente, uma cancelada."""
    return [
        tarefa(1, "alta", "concluida", horas_ate_concluir=2, horas_de_prazo=3),
        tarefa(2, "alta", "concluida", horas_ate_concluir=4, horas_de_prazo=3),
        tarefa(3, "media", "concluida", horas_ate_concluir=6, horas_de_prazo=8),
        tarefa(4, "baixa", "concluida", horas_ate_concluir=10, horas_de_prazo=9),
        tarefa(5, "media", "pendente"),
        tarefa(6, "baixa", "cancelada"),
    ]


def test_cenario_1_contagem_de_tarefas(cenario_1: list[Tarefa]) -> None:
    resultado = analyze_tasks(cenario_1)

    assert resultado["total_tarefas"] == 6
    assert resultado["total_concluidas"] == 4
    assert resultado["total_pendentes"] == 1


def test_cenario_1_tempo_medio_geral_em_horas(cenario_1: list[Tarefa]) -> None:
    # (2 + 4 + 6 + 10) / 4
    assert analyze_tasks(cenario_1)["tempo_medio_conclusao_horas"] == 5.5


def test_cenario_1_tempo_medio_por_prioridade(cenario_1: list[Tarefa]) -> None:
    assert analyze_tasks(cenario_1)["tempo_medio_por_prioridade_horas"] == {
        "alta": 3.0,
        "media": 6.0,
        "baixa": 10.0,
    }


def test_cenario_1_taxa_de_atraso(cenario_1: list[Tarefa]) -> None:
    # tarefas 2 e 4 terminaram depois do prazo: 2 de 4 concluídas
    assert analyze_tasks(cenario_1)["taxa_atraso_percentual"] == 50.0


def test_cenario_1_resultado_tem_exatamente_os_campos_do_contrato(
    cenario_1: list[Tarefa],
) -> None:
    assert set(analyze_tasks(cenario_1)) == {
        "total_tarefas",
        "total_concluidas",
        "total_pendentes",
        "tempo_medio_conclusao_horas",
        "tempo_medio_por_prioridade_horas",
        "taxa_atraso_percentual",
    }


# ------------------------------------------------------------------ Cenário 2, exceção


def test_cenario_2_data_conclusao_anterior_a_criacao_levanta_erro() -> None:
    invalida = tarefa(7, "alta", "concluida", horas_ate_concluir=-1)

    with pytest.raises(TaskValidationError, match=r"7.*data_conclusao"):
        analyze_tasks([invalida])


def test_cenario_2_erro_interrompe_a_analise_mesmo_com_tarefas_validas() -> None:
    validas = [tarefa(1, "alta", "concluida", horas_ate_concluir=2)]
    invalida = tarefa(8, "baixa", "concluida", horas_ate_concluir=-3)

    with pytest.raises(TaskValidationError, match=r"8.*data_conclusao"):
        analyze_tasks([*validas, invalida])
