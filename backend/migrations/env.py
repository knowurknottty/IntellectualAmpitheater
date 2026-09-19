from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from intelamp.database import Base
from intelamp import models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The default URL in alembic.ini is cwd-relative ("sqlite+aiosqlite:///./intelamp.sqlite3").
# Alembic must run from backend/ (its script_location is relative), so that default used to
# resolve to backend/intelamp.sqlite3 — a DIFFERENT database from the one the gateway uses
# (observed 2026-09-17: migration 0002 landed on backend/intelamp.sqlite3 while the live
# repo-root DB stayed at 0001_initial). Resolve any relative sqlite path against the repo
# root so migrations always land on the gateway's database unless INTELAMP_DATABASE_URL
# explicitly overrides it.
_url = os.environ.get("INTELAMP_DATABASE_URL")
if not _url:
    _url = config.get_main_option("sqlalchemy.url")
if _url and _url.startswith("sqlite") and "///./" in _url:
    _repo_root = Path(__file__).resolve().parents[2]
    _url = _url.replace("///./", f"///{_repo_root}/")
    config.set_main_option("sqlalchemy.url", _url)
elif _url:
    config.set_main_option("sqlalchemy.url", _url)

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
