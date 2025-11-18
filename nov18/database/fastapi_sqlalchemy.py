import os
import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker


class AsyncDatabase:
    def __init__(self):
        self.sessions = {}
        self.engines = {}
        self._lock = asyncio.Lock()

    async def get_sessions(self):
        """根据配置创建所有 sessionmaker 并返回"""
        async with self._lock:
            # 先清理旧的
            await self.dispose()

            self.sessions = {}
            self.engines = {}

            engine = create_async_engine(
                f"mysql+asyncmy://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
                f"{os.getenv('MYSQL_URL')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_USAGE_DB')}",
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
                future=True
            )
            self.engines[os.getenv('MYSQL_DB_NAME')] = engine
            self.sessions[os.getenv('MYSQL_DB_NAME')] = async_sessionmaker(
                engine, expire_on_commit=False
            )
            print("所有数据库连接已打开")
            return self.sessions

    async def dispose(self):
        """销毁所有 engine"""
        if self.engines:
            for engine in self.engines.values():
                await engine.dispose()
        self.engines.clear()
        self.sessions.clear()
        print("所有数据库连接已关闭")




