from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.services.schemas import (
    CreateServiceSchema,
    InputSLAServiceSchema,
    ServiceSchema,
    ServiceStateSchema,
    SLAServiceSchema,
)
from core.db import db_manager
from core.services.crud import ServiceCRUD, ServiceStateCRUD
from core.services.use_cases import (
    CreateServiceOrUpdateStateUseCase,
    DowntimeServiceUseCase,
)


router = APIRouter(tags=['Services'], prefix='/services')


@router.post('', response_model=ServiceSchema)
async def create_services_or_update_state(
    service: CreateServiceSchema, session: AsyncSession = Depends(db_manager.get_session)
):
    result = await CreateServiceOrUpdateStateUseCase(session, **service.model_dump()).action()
    return result


@router.get('', response_model=List[ServiceSchema])
async def list_services(session: AsyncSession = Depends(db_manager.get_session)):
    results = await ServiceCRUD(session).get_list()
    return results


@router.post('/{service_name:str}/sla', response_model=SLAServiceSchema)
async def sla_service(
    service_name: str,
    time_interval: InputSLAServiceSchema,
    session: AsyncSession = Depends(db_manager.get_session),
):
    service_repo = ServiceCRUD(session)

    if not await service_repo.exist_by_name(service_name):
        raise HTTPException(status_code=404, detail={'message': f'Сервис {service_name} не существует.'})

    downtime, sla = await DowntimeServiceUseCase(
        db_session=session, service_name=service_name, **time_interval.model_dump()
    ).action()

    return SLAServiceSchema(downtime=downtime, sla=sla)


@router.get('/{service_name:str}/states', response_model=List[ServiceStateSchema])
async def list_service_statuses(
    service_name: str,
    session: AsyncSession = Depends(db_manager.get_session),
):
    service_repo = ServiceCRUD(session)
    service_state_repo = ServiceStateCRUD(session)

    if not await service_repo.exist_by_name(service_name):
        raise HTTPException(
            status_code=404,
            detail={'message': f'Сервис "{service_name}" не существует.'},
        )

    results = await service_state_repo.get_list_by_service_name(service_name)
    return results
