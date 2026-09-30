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


# ------------------------------------------------------------------ casos de borda

ZERADO_POR_PRIORIDADE = {"alta": 0.0, "media": 0.0, "baixa": 0.0}


def test_borda_lista_vazia_devolve_zeros_sem_excecao() -> None:
    assert analyze_tasks([]) == {
        "total_tarefas": 0,
        "total_concluidas": 0,
        "total_pendentes": 0,
        "tempo_medio_conclusao_horas": 0.0,
        "tempo_medio_por_prioridade_horas": ZERADO_POR_PRIORIDADE,
        "taxa_atraso_percentual": 0.0,
    }


def test_borda_apenas_pendentes_devolve_zeros_sem_excecao() -> None:
    pendentes = [tarefa(i, "media", "pendente") for i in (1, 2, 3)]

    assert analyze_tasks(pendentes) == {
        "total_tarefas": 3,
        "total_concluidas": 0,
        "total_pendentes": 3,
        "tempo_medio_conclusao_horas": 0.0,
        "tempo_medio_por_prioridade_horas": ZERADO_POR_PRIORIDADE,
        "taxa_atraso_percentual": 0.0,
    }


# ------------------------------------------------------------------ complementares


def test_c01_conclusao_exatamente_no_prazo_nao_e_atraso() -> None:
    no_prazo = tarefa(1, "alta", "concluida", horas_ate_concluir=5, horas_de_prazo=5)
    um_minuto_depois = tarefa(
        2, "alta", "concluida", horas_ate_concluir=5 + 1 / 60, horas_de_prazo=5
    )

    assert analyze_tasks([no_prazo, um_minuto_depois])["taxa_atraso_percentual"] == 50.0


@pytest.mark.parametrize("prioridade", ["urgente", "", "altissima"])
def test_c02_prioridade_invalida_levanta_erro(prioridade: str) -> None:
    with pytest.raises(TaskValidationError, match="prioridade"):
        analyze_tasks([tarefa(1, prioridade, "pendente")])


def test_c03_prioridade_em_maiusculas_e_aceita() -> None:
    resultado = analyze_tasks([tarefa(1, "ALTA", "concluida", horas_ate_concluir=4)])

    assert resultado["tempo_medio_por_prioridade_horas"]["alta"] == 4.0


def test_c04_data_sem_fuso_levanta_erro() -> None:
    sem_fuso = Tarefa(
        id_tarefa=1,
        data_criacao=datetime(2026, 9, 1, 8, 0),
        prazo=INICIO + timedelta(hours=8),
        prioridade="alta",
        status="pendente",
    )

    with pytest.raises(TaskValidationError, match="data_criacao"):
        analyze_tasks([sem_fuso])


def test_c05_concluida_sem_data_conclusao_levanta_erro() -> None:
    with pytest.raises(TaskValidationError, match=r"1.*data_conclusao"):
        analyze_tasks([tarefa(1, "alta", "concluida", horas_ate_concluir=None)])


@pytest.mark.parametrize("ids", [(1, 1), (0,), (-4,)])
def test_c06_id_repetido_ou_nao_positivo_levanta_erro(ids: tuple[int, ...]) -> None:
    with pytest.raises(TaskValidationError, match="id_tarefa"):
        analyze_tasks([tarefa(i, "alta", "pendente") for i in ids])


@pytest.mark.parametrize("status", ["finalizada", "Concluida", ""])
def test_c07_status_invalido_levanta_erro(status: str) -> None:
    with pytest.raises(TaskValidationError, match="status"):
        analyze_tasks([tarefa(1, "alta", status, horas_ate_concluir=2)])


def test_c08_media_arredondada_em_duas_casas() -> None:
    tarefas = [
        tarefa(1, "baixa", "concluida", horas_ate_concluir=1),
        tarefa(2, "baixa", "concluida", horas_ate_concluir=2),
        tarefa(3, "baixa", "concluida", horas_ate_concluir=2),
    ]

    # 5 / 3 = 1.666...
    assert analyze_tasks(tarefas)["tempo_medio_conclusao_horas"] == 1.67


def test_c09_nao_altera_a_lista_recebida(cenario_1: list[Tarefa]) -> None:
    copia = copy.deepcopy(cenario_1)

    analyze_tasks(cenario_1)

    assert cenario_1 == copia


def test_c10_data_inicio_anterior_a_criacao_levanta_erro() -> None:
    inicio_invalido = Tarefa(
        id_tarefa=9,
        data_criacao=INICIO,
        prazo=INICIO + timedelta(hours=8),
        prioridade="media",
        status="pendente",
        data_inicio=INICIO - timedelta(hours=1),
    )

    with pytest.raises(TaskValidationError, match=r"9.*data_inicio"):
        analyze_tasks([inicio_invalido])
