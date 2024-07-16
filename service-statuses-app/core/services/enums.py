from enum import Enum


class ServiceStatusEnum(Enum):
    """
    Возможные состояния сервисов
    """

    WORK = 'WORK'  # сервис работает
    NOT_WORK = 'NOT_WORK'  # сервис не работает
    UNSTABLE = 'UNSTABLE'  # сервис работает не стабильно
