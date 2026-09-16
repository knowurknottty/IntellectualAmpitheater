from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from intelamp.database import Base
from intelamp import models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

if url := os.environ.get("INTELAMP_DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_connection: context.configure(
                connection=sync_connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
        )
        async with connectable.begin() as transaction_connection:
            await transaction_connection.run_sync(
                lambda sync_connection: context.configure(
                    connection=sync_connection,
                    target_metadata=target_metadata,
                    compare_type=True,
                )
            )
            await transaction_connection.run_sync(lambda _: context.run_migrations())
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
