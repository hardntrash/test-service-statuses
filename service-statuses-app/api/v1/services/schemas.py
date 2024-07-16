import datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from core.services.enums import ServiceStatusEnum


class BaseServiceSchema(BaseModel):
    name: str = Field(description='Наименование')
    status: ServiceStatusEnum = Field(description='Текущее состояние')


class CreateServiceSchema(BaseServiceSchema):
    description: str = Field(description='Описание')


class ServiceSchema(BaseServiceSchema):
    id: int


class ServiceStateSchema(BaseModel):
    id: int
    status: ServiceStatusEnum = Field(description='Состояние сервиса')
    description: str = Field(description='Описание')
    time_in: datetime.datetime = Field(description='Время начало')
    time_out: datetime.datetime | None = Field(description='Время конца')
    service_id: int = Field(description='Идентификатор сервиса')


class InputSLAServiceSchema(BaseModel):
    from_time: datetime.datetime = Field(description='Начало интервала')
    to_time: datetime.datetime = Field(description='Конец интервала')

    @model_validator(mode='after')
    def check_interval_values(self) -> Self:
        if self.from_time > self.to_time:
            raise ValueError('Начало интервала не может быть больше Конца')
        return self


class SLAServiceSchema(BaseModel):
    sla: float = Field(description='Процент SLA', ge=0.0, le=100.0)
    downtime: str = Field(description='Время, в течении которого не работал сервис')
