import logging
from typing import Any, List, Literal, Type, TypeVar
from uuid import uuid4

from sqlalchemy import and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select

from app.core.config import DATABASE_URL
from app.models.db_source.db_tables import Base


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T")


class AsyncDatabaseAdapter:
    def __init__(self, database_url: str = DATABASE_URL) -> None:
        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            connect_args={
                "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
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

    async def get_by_values(
        self,
        model: Type[T],
        and_conditions: dict = None,
        or_conditions: dict = None,
        mode: Literal["and", "or", "mixed"] = "and",
    ) -> List[T]:
        async with self.SessionLocal() as session:
            query = select(model)

            and_conditions = and_conditions or {}
            or_conditions = or_conditions or {}

            def validate_keys(conditions):
                for key in conditions:
                    if not hasattr(model, key):
                        raise ValueError(f"Invalid field: {key}")

            validate_keys(and_conditions)
            validate_keys(or_conditions)

            and_clauses = [getattr(model, k) == v for k, v in and_conditions.items()]
            or_clauses = [getattr(model, k) == v for k, v in or_conditions.items()]

            if mode == "and":
                if and_clauses:
                    query = query.where(and_(*and_clauses))
            elif mode == "or":
                if or_clauses:
                    query = query.where(or_(*or_clauses))
            elif mode == "mixed":
                combined = []
                if and_clauses:
                    combined.append(and_(*and_clauses))
                if or_clauses:
                    combined.append(or_(*or_clauses))
                if combined:
                    query = query.where(and_(*combined))

            result = await session.execute(query)
            return result.scalars().all()

    async def insert(self, model, insert_dict: dict) -> Any:
        async with self.SessionLocal() as session:
            record = model(**insert_dict)
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record

    async def update_by_id(self, model, record_id: int, updates: dict):
        async with self.SessionLocal() as session:
            stmt = update(model).where(model.id == record_id).values(**updates)
            await session.execute(stmt)
            await session.commit()

    async def update_by_value(self, model, param: str, param_val: any, updates: dict):
        async with self.SessionLocal() as session:
            stmt = (
                update(model)
                .where(getattr(model, param) == param_val)
                .values(**updates)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

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
