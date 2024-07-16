from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, func, select, String, TIMESTAMP
from sqlalchemy.orm import column_property, Mapped, mapped_column, relationship

from core.db import BaseModel
from core.services.enums import ServiceStatusEnum


class ServiceState(BaseModel):
    """
    Модель состояний сервисов
    """

    __tablename__ = 'service_statuses'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[ServiceStatusEnum]
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    description: Mapped[str] = mapped_column(String(120))

    service_id: Mapped[int] = mapped_column(ForeignKey('services.id', ondelete='CASCADE'))
    service: Mapped['Service'] = relationship(back_populates='states')

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.service} - {self.status} - {self.start_time} - {self.end_time}'


class Service(BaseModel):
    """
    Модель сервисов
    """

    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)

    states: Mapped[List[ServiceState]] = relationship(back_populates='service')
    status: Mapped[ServiceStatusEnum] = column_property(
        select(ServiceState.status)
        .where(ServiceState.service_id == id)
        .order_by(ServiceState.start_time.desc())
        .limit(1)
        .correlate_except(ServiceState)
        .scalar_subquery()
    )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'Сервис: {self.name}'
