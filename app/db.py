from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.exc import SQLAlchemyError

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:123456qwe@localhost/fastly"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, future=True
)

SessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    session = SessionLocal()
    try:
        yield session
    except SQLAlchemyError as ex:
        await session.rollback()
        raise ex
    finally:
        await session.close()
