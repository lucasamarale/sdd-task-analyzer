"""TaskAnalyzer: métricas de produtividade a partir de um conjunto de tarefas.

Implementa o contrato de specs/task_analyzer_spec.md, versão 1.1, sob as regras de
CONTEXT_RULES.md. A função pública é analyze_tasks. Toda entrada é validada antes de
qualquer cálculo, e nenhuma divisão acontece sem verificar o denominador.
"""

import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

logger = logging.getLogger(__name__)

PRIORIDADES: tuple[str, ...] = ("alta", "media", "baixa")
STATUS_VALIDOS: frozenset[str] = frozenset({"concluida", "pendente", "cancelada"})
SEGUNDOS_POR_HORA = 3600
CASAS_DECIMAIS = 2


class TaskValidationError(ValueError):
    """Entrada que viola o contrato de specs/task_analyzer_spec.md, seção 1.4."""


@dataclass(frozen=True)
class Tarefa:
    """Uma tarefa de entrada, conforme a seção 1.2.1 da especificação.

    Attributes:
        id_tarefa: Identificador inteiro positivo, único no conjunto.
        data_criacao: Abertura da tarefa, ciente de fuso.
        prazo: Limite para a conclusão, ciente de fuso.
        prioridade: "baixa", "media" ou "alta", sem distinção de maiúsculas.
        status: "concluida", "pendente" ou "cancelada".
        data_inicio: Início da execução, opcional.
        data_conclusao: Conclusão, obrigatória quando o status é "concluida".
    """

    id_tarefa: int
    data_criacao: datetime
    prazo: datetime
    prioridade: str
    status: str
    data_inicio: datetime | None = None
    data_conclusao: datetime | None = None


class ResultadoAnalise(TypedDict):
    """Resultado de analyze_tasks, conforme a seção 1.2.2 da especificação."""

    total_tarefas: int
    total_concluidas: int
    total_pendentes: int
    tempo_medio_conclusao_horas: float
    tempo_medio_por_prioridade_horas: dict[str, float]
    taxa_atraso_percentual: float


def analyze_tasks(tarefas: list[Tarefa]) -> ResultadoAnalise:
    """Calcula métricas de produtividade a partir de um conjunto de tarefas.

    Args:
        tarefas: Tarefas a analisar. A lista não é alterada.

    Returns:
        Totais por status, tempo médio de conclusão em horas, geral e por prioridade,
        e taxa de atraso em percentual. Sem tarefa concluída, médias e taxa valem 0.0.

    Raises:
        TaskValidationError: Se alguma tarefa violar o contrato de entrada.
    """
    _validar_conjunto(tarefas)

    concluidas = [tarefa for tarefa in tarefas if tarefa.status == "concluida"]
    resultado = ResultadoAnalise(
        total_tarefas=len(tarefas),
        total_concluidas=len(concluidas),
        total_pendentes=sum(1 for tarefa in tarefas if tarefa.status == "pendente"),
        tempo_medio_conclusao_horas=_arredondar(_media_horas(concluidas)),
        tempo_medio_por_prioridade_horas={
            prioridade: _arredondar(_media_horas(_da_prioridade(concluidas, prioridade)))
            for prioridade in PRIORIDADES
        },
        taxa_atraso_percentual=_arredondar(_taxa_atraso(concluidas)),
    )
    logger.info(
        "Análise concluída: %d tarefas, %d concluídas, %d pendentes",
        resultado["total_tarefas"],
        resultado["total_concluidas"],
        resultado["total_pendentes"],
    )
    return resultado


# ------------------------------------------------------------------ validação


def _validar_conjunto(tarefas: Sequence[Tarefa]) -> None:
    """Valida todas as tarefas e a unicidade dos identificadores, antes de calcular."""
    ids_vistos: set[int] = set()
    for tarefa in tarefas:
        _validar_tarefa(tarefa)
        if tarefa.id_tarefa in ids_vistos:
            raise _erro(tarefa.id_tarefa, "id_tarefa", "identificador repetido no conjunto")
        ids_vistos.add(tarefa.id_tarefa)


def _validar_tarefa(tarefa: Tarefa) -> None:
    """Aplica à tarefa as regras da seção 1.4 da especificação."""
    identificador = tarefa.id_tarefa
    # bool é subclasse de int em Python, mas não é um identificador válido
    if isinstance(identificador, bool) or not isinstance(identificador, int) or identificador < 1:
        raise _erro(identificador, "id_tarefa", "deve ser um inteiro positivo")

    if not isinstance(tarefa.prioridade, str) or tarefa.prioridade.lower() not in PRIORIDADES:
        raise _erro(identificador, "prioridade", f"valores aceitos: {', '.join(PRIORIDADES)}")

    if tarefa.status not in STATUS_VALIDOS:
        raise _erro(identificador, "status", f"valores aceitos: {', '.join(sorted(STATUS_VALIDOS))}")

    _validar_data(identificador, "data_criacao", tarefa.data_criacao)
    _validar_data(identificador, "prazo", tarefa.prazo)
    for campo, data in (("data_inicio", tarefa.data_inicio), ("data_conclusao", tarefa.data_conclusao)):
        if data is not None:
            _validar_data(identificador, campo, data)
            if data < tarefa.data_criacao:
                raise _erro(identificador, campo, "não pode ser anterior a data_criacao")

    if tarefa.status == "concluida" and tarefa.data_conclusao is None:
        raise _erro(identificador, "data_conclusao", "obrigatória para tarefa concluída")


def _validar_data(identificador: int, campo: str, valor: object) -> None:
    """Exige um datetime ciente de fuso."""
    if not isinstance(valor, datetime):
        raise _erro(identificador, campo, "deve ser datetime")
    if valor.tzinfo is None or valor.utcoffset() is None:
        raise _erro(identificador, campo, "deve ser ciente de fuso")


def _erro(identificador: object, campo: str, motivo: str) -> TaskValidationError:
    """Monta a exceção com o identificador da tarefa e o campo responsável."""
    return TaskValidationError(f"Tarefa {identificador}: campo {campo} inválido, {motivo}.")


# ------------------------------------------------------------------ cálculo


def _da_prioridade(tarefas: Iterable[Tarefa], prioridade: str) -> list[Tarefa]:
    """Filtra as tarefas de uma prioridade, sem distinção de maiúsculas."""
    return [tarefa for tarefa in tarefas if tarefa.prioridade.lower() == prioridade]


def _horas_ate_concluir(tarefa: Tarefa) -> float:
    """Tempo entre a criação e a conclusão, em horas, sem arredondar."""
    assert tarefa.data_conclusao is not None  # garantido pela validação
    return (tarefa.data_conclusao - tarefa.data_criacao).total_seconds() / SEGUNDOS_POR_HORA


def _media_horas(concluidas: Sequence[Tarefa]) -> float:
    """Média de horas até concluir, ou 0.0 se não houver tarefa (RN-08 e RN-09)."""
    if not concluidas:
        return 0.0
    return sum(_horas_ate_concluir(tarefa) for tarefa in concluidas) / len(concluidas)


def _taxa_atraso(concluidas: Sequence[Tarefa]) -> float:
    """Percentual concluído estritamente depois do prazo, ou 0.0 sem concluídas."""
    if not concluidas:
        return 0.0
    atrasadas = sum(
        1
        for tarefa in concluidas
        if tarefa.data_conclusao is not None and tarefa.data_conclusao > tarefa.prazo
    )
    return atrasadas / len(concluidas) * 100


def _arredondar(valor: float) -> float:
    """Arredonda na montagem da saída, nunca antes (RN-05)."""
    return round(valor, CASAS_DECIMAIS)
