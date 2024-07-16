from enum import Enum as PyEnum

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import ENUM as PGENUM
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )
    type_annotation_map = {
        PyEnum: PGENUM(PyEnum),
    }
