from typing import Literal

import psycopg2
from django.conf import settings
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

Outcome = Literal["exists", "created"]


def ensure_default_database_exists(maintenance_dbname: str = "postgres") -> Outcome:
    """
    Подключается к служебной базе и создаёт DATABASES['default']['NAME'], если её нет.
    """
    db = settings.DATABASES["default"]
    target_name = db["NAME"]

    conn_kw = {
        "dbname": maintenance_dbname,
        "user": db["USER"],
        "password": db["PASSWORD"],
        "host": db["HOST"],
        "port": db["PORT"] or "5432",
    }
    opts = db.get("OPTIONS") or {}
    if opts.get("sslmode"):
        conn_kw["sslmode"] = opts["sslmode"]

    conn = psycopg2.connect(**conn_kw)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (target_name,),
            )
            if cur.fetchone():
                return "exists"
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_name))
            )
            return "created"
    finally:
        conn.close()
