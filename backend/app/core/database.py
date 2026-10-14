import os
from collections.abc import Iterator
from contextlib import contextmanager
from threading import Lock

import certifi
from mysql.connector.pooling import MySQLConnectionPool

_pool: MySQLConnectionPool | None = None
_pool_lock = Lock()


def connect():
    global _pool
    with _pool_lock:
        if _pool is None:
            _pool = MySQLConnectionPool(
                pool_size=5,
                host=os.environ["MYSQL_HOST"],
                port=int(os.getenv("MYSQL_PORT", "3306")),
                database=os.environ["MYSQL_DATABASE"],
                user=os.environ["MYSQL_USER"],
                password=os.environ["MYSQL_PASSWORD"],
                ssl_disabled=False,
                ssl_verify_cert=True,
                ssl_verify_identity=True,
                ssl_ca=os.getenv("MYSQL_SSL_CA") or certifi.where(),
            )
    return _pool.get_connection()


@contextmanager
def database() -> Iterator:
    connection = connect()
    try:
        yield connection
    finally:
        connection.close()
