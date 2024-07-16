import datetime
from typing import Sequence

from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.services.models import Service, ServiceState


class ServiceStateCRUD:
    """
    Класс для CRUD операций с Состояниями сервисов
    """

    def __init__(self, db_session: AsyncSession):
        """
        :param db_session: объект сессии БД
        """
        self._db_session = db_session

    async def create(self, status: str, description: str, service_id: int) -> ServiceState:
        """
        Метод для создания Состояния сервиса
        :param status: статус сервиса
        :param description: описания состояния
        :param service_id: идентификатор сервиса
        :return: Состояние сервиса
        """
        new_state = ServiceState(status=status, service_id=service_id, description=description)
        self._db_session.add(new_state)

        if previous_state := await self.get_last_by_service_id(service_id):
            # вызываем flush() чтобы получить значение Времени начала нового состояния и использовать его
            # как значение Времени конца для предыдущего состояния
            await self._db_session.flush()
            previous_state.end_time = new_state.start_time
            self._db_session.add(new_state)

        await self._db_session.commit()
        await self._db_session.refresh(new_state)
        return new_state

    async def get_last_by_service_id(self, service_id: int) -> ServiceState:
        """
        Метод для получения последнего последнего Состояния сервиса
        :param service_id: идентификатор Сервиса
        :return: Состояние сервиса
        """
        query = (
            select(ServiceState)
            .where(ServiceState.service_id == service_id)
            .order_by(ServiceState.start_time.desc())
            .limit(1)
        )
        result = await self._db_session.execute(query)
        return result.scalar()

    async def get_list_by_service_name(self, service_name: str) -> Sequence[ServiceState]:
        """
        Метод для получения списка Состояний сервиса по наименованию
        :param service_name: Наименование сервиса
        :return: список Состояний сервиса
        """
        query = (
            select(ServiceState)
            .join(Service)
            .where(Service.name == service_name)
            .order_by(ServiceState.start_time.desc())
        )
        service_states = await self._db_session.execute(query)
        return service_states.scalars().all()

    async def get_list_by_service_name_and_time_interval(
        self,
        service_name: str,
        from_time: datetime.datetime,
        to_time: datetime.datetime,
    ) -> Sequence[ServiceState]:
        """
        Метод для получения Состояний сервиса по наименованию и временному интервала
        :param service_name: Наименование сервиса
        :param from_time: начало временного интервала
        :param to_time: конец временного интервала
        :return: список Состояний сервиса
        """
        query = (
            select(ServiceState)
            .join(Service)
            .where(
                Service.name == service_name,
                or_(
                    ServiceState.end_time >= from_time,
                    ServiceState.end_time.is_(None),
                ),
                ServiceState.start_time <= to_time,
            )
            .order_by(ServiceState.start_time.desc())
        )
        service_states = await self._db_session.execute(query)
        return service_states.scalars().all()


class ServiceCRUD:
    """
    Класс для CRUD операций с Сервисами
    """

    def __init__(self, db_session: AsyncSession):
        """
        :param db_session: сессия БД
        """
        self._db_session = db_session

    async def create(self, name: str) -> Service:
        """
        Метод для создания Сервиса
        :param name: наименование сервиса
        :return: Сервис
        """
        service = Service(name=name)
        self._db_session.add(service)
        await self._db_session.commit()
        await self._db_session.refresh(service)
        return service

    async def get_list(self) -> Sequence[Service]:
        """
        Метод для получения списка Сервисов
        :return: список Сервисов
        """
        query = select(Service)
        services = await self._db_session.execute(query)
        return services.scalars().all()

    async def get_by_name(self, service_name: str) -> Service:
        """
        Метод для получения Сервиса по наименованию
        :param service_name: наименование
        :return: Сервис
        """
        query = select(Service).where(Service.name == service_name)
        service = await self._db_session.execute(query)
        return service.scalar()

    async def exist_by_name(self, service_name: str) -> bool:
        """
        Метод для проверки существования Сервиса по наименованию
        :param service_name: наименование
        :return: True - если Сервис существует, иначе False
        """
        query = exists(Service.name).where(Service.name == service_name).select()
        return await self._db_session.scalar(query)
