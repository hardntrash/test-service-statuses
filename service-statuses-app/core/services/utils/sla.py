import datetime
from typing import Sequence

from core.services.enums import ServiceStatusEnum
from core.services.models import ServiceState


def calc_service_downtime(service_states: Sequence[ServiceState]) -> datetime.timedelta:
    """
    Функция для расчета длительность недоступности сервиса
    :param service_states: список Состояний сервиса
    :return: длительность недоступности сервиса
    """
    downtime_counter = datetime.timedelta()

    for service_state in service_states:
        if service_state.status == ServiceStatusEnum.NOT_WORK:
            downtime_counter += service_state.end_time - service_state.start_time

    return downtime_counter


def calc_service_sla(downtime: datetime.timedelta, from_time: datetime.datetime, to_time: datetime.datetime) -> float:
    """
    Функция для расчета процента SLA
    :param downtime: длительность недоступности Сервиса
    :param from_time: начало временного интервала
    :param to_time: начало временного интервала
    :return: процент SLA
    """
    time_interval = to_time - from_time
    return (time_interval - downtime) / time_interval * 100
