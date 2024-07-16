import datetime
from typing import Sequence, Tuple, Type

from sqlalchemy.ext.asyncio import AsyncSession

from core.services.crud import ServiceCRUD, ServiceStateCRUD
from core.services.models import Service, ServiceState
from core.services.utils.sla import calc_service_downtime, calc_service_sla


class CreateServiceOrUpdateStateUseCase:
    """
    UseCase для создания Сервисов и их состояний
    """

    def __init__(
        self,
        db_session: AsyncSession,
        name: str,
        status: str,
        description: str,
        service_repository: Type[ServiceCRUD] = ServiceCRUD,
        service_state_repository: Type[ServiceStateCRUD] = ServiceStateCRUD,
    ):
        self._db_session = db_session
        self._service_repository = service_repository(db_session)
        self._service_state_repository = service_state_repository(db_session)

        self._name = name
        self._status = status
        self._description = description

    async def _get_or_create_service(self, name: str) -> Service:
        service = await self._service_repository.get_by_name(name) or await self._service_repository.create(name)
        return service

    async def action(self) -> Service:
        service = await self._get_or_create_service(self._name)
        await self._service_state_repository.create(
            service_id=service.id,
            status=self._status,
            description=self._description,
        )
        await self._db_session.refresh(service)
        return service


class DowntimeServiceUseCase:
    """
    UseCase для расчета длительности недоступности сервиса и его процента SLA
    """

    def __init__(
        self,
        db_session: AsyncSession,
        service_name: str,
        from_time: datetime.datetime,
        to_time: datetime.datetime,
        service_state_repository: Type[ServiceStateCRUD] = ServiceStateCRUD,
    ):
        self._db_session = db_session
        self._service_state_repository = service_state_repository(db_session)

        self._service_name = service_name
        self._from_time = from_time
        self._to_time = to_time

    async def _get_list_service_states(self) -> Sequence[ServiceState]:
        """
        Метод для получения списка Состояний сервиса по временному интервалу
        :return: список Состояний сервиса
        """
        service_states = await self._service_state_repository.get_list_by_service_name_and_time_interval(
            self._service_name,
            self._from_time,
            self._to_time,
        )
        return service_states

    def _prepare_data(self, service_states: Sequence[ServiceState]) -> None:
        """
        Метод для подготовки данных к расчетам длительности недоступности сервиса и процента SLA
        """
        # сортируем список Состояний сервиса, на тот случай если данные были переданы неотсортированными
        service_states = sorted(service_states, key=lambda service_state_: service_state_.start_time)

        first_state = service_states[0]
        last_state = service_states[-1]

        if first_state.start_time < self._from_time:
            first_state.start_time = self._from_time
        else:
            self._from_time = first_state.start_time

        if not last_state.end_time:
            last_state.end_time = last_state.start_time

        if last_state.end_time > self._to_time:
            last_state.end_time = self._to_time
        else:
            self._to_time = last_state.end_time

    async def action(self) -> Tuple[str, float]:
        """
        Метод для получения длительности недоступности сервиса и процента SLA
        :return: (длительность недоступности сервиса, процент SLA)
        """
        service_states = await self._get_list_service_states()
        self._prepare_data(service_states)
        downtime = calc_service_downtime(service_states)
        sla = calc_service_sla(downtime, self._from_time, self._to_time)
        return str(downtime), round(sla, 3)
