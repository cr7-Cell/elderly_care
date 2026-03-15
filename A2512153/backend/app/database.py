from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings
import os

# 使用MySQL数据库，从环境变量或配置中获取
database_url = os.getenv('DATABASE_URL', settings.DATABASE_URL)

# 创建异步引擎
# pool_size: 连接池大小（减少连接数）
# max_overflow: 最大溢出连接数
# pool_pre_ping: 连接前检查连接是否有效
engine = create_async_engine(
    database_url,
    echo=True,
    future=True,
    pool_size=5,  # 减少连接池大小
    max_overflow=10,  # 减少最大溢出连接
    pool_pre_ping=True,  # 连接前检查
    pool_recycle=3600,  # 连接回收时间（秒）
)

# 创建异步会话
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


# 依赖注入：获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

