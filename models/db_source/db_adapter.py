from uuid import uuid4
from typing import Any, List
import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from config import DATABASE_URL
from models.tables.db_tables import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncDatabaseAdapter:
    def __init__(self, database_url: str = DATABASE_URL) -> None:
        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            connect_args={
                "prepared_statement_name_func": lambda:  f"__asyncpg_{uuid4()}__",
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            },
    )
        self.SessionLocal = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize_tables(self) -> None:
        logger.info("Tables are created or exists")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_all(self, model) -> List[Any]:
        async with self.SessionLocal() as session:
            result = await session.execute(select(model))
            return result.scalars().all()

    async def get_by_id(self, model, id) -> Any:
        async with self.SessionLocal() as session:
            result = await session.execute(select(model).where(model.id == id))
            return result.scalar_one_or_none()

    async def get_by_value(self, model, parameter: str, parameter_value: Any) -> List[Any]:
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(model).where(getattr(model, parameter) == parameter_value)
            )
            return result.scalars().all()

    async def get_by_values(self, model, conditions: dict) -> List[Any]:
        async with self.SessionLocal() as session:
            query = select(model)
            for key, value in conditions.items():
                query = query.where(getattr(model, key) == value)
            result = await session.execute(query)
            return result.scalars().all()

    async def insert(self, model, insert_dict: dict) -> Any:
        async with self.SessionLocal() as session:
            record = model(**insert_dict)
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record

    async def update(self, model, update_dict: dict, id: int) -> Any:
        async with self.SessionLocal() as session:
            result = await session.execute(select(model).where(model.id == id))
            record = result.scalar_one_or_none()
            if record:
                for key, value in update_dict.items():
                    setattr(record, key, value)
                await session.commit()
            return record

    async def update_by_id(self, model, record_id: int, updates: dict):
        async with self.SessionLocal() as session:
            stmt = update(model).where(model.id == record_id).values(**updates)
            await session.execute(stmt)
            await session.commit()

    async def delete(self, model, id: int) -> Any:
        async with self.SessionLocal() as session:
            result = await session.execute(select(model).where(model.id == id))
            record = result.scalar_one_or_none()
            if record:
                await session.delete(record)
                await session.commit()
            return record

    async def delete_by_value(self, model, parameter: str, parameter_value: Any) -> List[Any]:
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(model).where(getattr(model, parameter) == parameter_value)
            )
            records = result.scalars().all()
            for record in records:
                await session.delete(record)
            await session.commit()
            return records

    async def execute_with_request(self, request) -> List[Any]:
        async with self.SessionLocal() as session:
            result = await session.execute(request)
            await session.commit()
            return result.fetchall()


adapter = AsyncDatabaseAdapter()
