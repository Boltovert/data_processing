import importlib
import os
import pkgutil
from importlib.resources import Package
from logging.config import fileConfig
from pathlib import Path
from typing import Any

import sqlalchemy
from alembic import context
from alembic.script import write_hooks, ScriptDirectory

import src
from src.core.models_base import Base
from src.settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def import_models_modules(package: Package):
    package_name = package.__name__
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package_name + "."):
        if is_pkg:
            try:
                subpackage = importlib.import_module(module_name)
                import_models_modules(subpackage)
            except Exception:
                pass
        elif module_name.endswith(".models"):
            importlib.import_module(module_name)


def run_migrations_online() -> None:
    url = sqlalchemy.make_url(settings.postgres.uri).set(drivername="postgresql+psycopg")
    engine = sqlalchemy.create_engine(url)

    with engine.begin() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


@write_hooks.register("update_last_version")
def update_last_version(*_: Any, **__: Any) -> None:
    last_version_file = Path(os.getcwd()) / "migrations" / "last_version.txt"
    script_dir = ScriptDirectory.from_config(config)
    heads = script_dir.get_heads()

    if len(heads) > 1:
        print(
            f"\033[91mMigration tree contains multiple heads ({len(heads)}), "
            f"fix this by merging a heads and generating sequential revisions before commiting!\033[0m"
        )

    latest_revision = heads[0]

    with open(last_version_file, "w") as f:
        f.write(latest_revision + "\n")


import_models_modules(src)
run_migrations_online()
