from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Any
from models.tables.db_tables import Base
from config import DATABASE_URL


class DatabaseAdapter:
    def __init__(self, database_url: str = DATABASE_URL) -> None:
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.connection = None

    def connect(self) -> None:
        try:
            self.connection = self.SessionLocal()
            print("Соединение с базой данных установлено.")
        except SQLAlchemyError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def initialize_tables(self) -> None:
        print("Таблицы созданы или уже существуют")
        Base.metadata.create_all(bind=self.engine)

    def get_all(self, model) -> List[dict]:
        with self.SessionLocal() as session:
            return session.query(model).all()

    def get_by_id(self, model, id: int) -> List[dict]:
        with self.SessionLocal() as session:
            return session.query(model).filter(model.id == id).first()

    def get_by_value(self, model, parameter: str, parameter_value: Any) -> List[dict]:
        with self.SessionLocal() as session:
            return (
                session.query(model)
                .filter(getattr(model, parameter) == parameter_value)
                .all()
            )

    def insert(self, model, insert_dict: dict) -> List[dict]:
        with self.SessionLocal() as session:
            record = model(**insert_dict)
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def update(self, model, update_dict: dict, id: int) -> List[dict]:
        with self.SessionLocal() as session:
            record = session.query(model).filter(model.id == id).first()
            for key, value in update_dict.items():
                setattr(record, key, value)
            session.commit()
            return record

    def delete(self, model, id) -> List[dict]:
        with self.SessionLocal() as session:
            record = session.query(model).filter(model.id == id).first()
            session.delete(record)
            session.commit()
            return record

    def execute_with_request(self, request: str) -> List[dict]:
        with self.SessionLocal() as session:
            result = session.execute(request)
            session.commit()
            return result.fetchall()

    def delete_by_value(
        self, model, parameter: str, parameter_value: Any
    ) -> List[dict]:
        with self.SessionLocal() as session:
            records = (
                session.query(model)
                .filter(getattr(model, parameter) == parameter_value)
                .all()
            )
            for record in records:
                session.delete(record)
            session.commit()
            return records

    def get_by_values(self, model, conditions: dict):
        with self.SessionLocal() as session:
            query = session.query(model)
            for key, value in conditions.items():
                query = query.filter(getattr(model, key) == value)
            return query.all()


adapter = DatabaseAdapter()
