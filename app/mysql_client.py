import logging
import threading
from typing import Any, Dict, List, Optional

from .config import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB,
    MYSQL_CHARSET, MYSQL_POOL_MIN, MYSQL_POOL_MAX,
    MYSQL_CONNECT_TIMEOUT, MYSQL_READ_TIMEOUT,
)

logger = logging.getLogger(__name__)

_pool: Optional["_ConnectionPool"] = None
_pool_lock = threading.Lock()


def _get_pool() -> "_ConnectionPool":
    global _pool
    if _pool is not None:
        return _pool
    with _pool_lock:
        if _pool is None:
            _pool = _ConnectionPool(
                host=MYSQL_HOST, port=MYSQL_PORT,
                user=MYSQL_USER, password=MYSQL_PASSWORD,
                database=MYSQL_DB, charset=MYSQL_CHARSET,
                pool_min=MYSQL_POOL_MIN, pool_max=MYSQL_POOL_MAX,
                connect_timeout=MYSQL_CONNECT_TIMEOUT,
                read_timeout=MYSQL_READ_TIMEOUT,
            )
    return _pool


class _ConnectionPool:
    def __init__(self, host: str, port: int, user: str, password: str,
                 database: str, charset: str, pool_min: int, pool_max: int,
                 connect_timeout: int, read_timeout: int):
        import pymysql
        self._pymysql = pymysql
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._charset = charset
        self._connect_timeout = connect_timeout
        self._read_timeout = read_timeout
        self._pool_min = pool_min
        self._pool_max = pool_max
        self._available: List[pymysql.Connection] = []
        self._used_count = 0
        self._lock = threading.Lock()

    def _make_conn(self):
        return self._pymysql.connect(
            host=self._host, port=self._port,
            user=self._user, password=self._password,
            database=self._database, charset=self._charset,
            connect_timeout=self._connect_timeout,
            read_timeout=self._read_timeout,
            cursorclass=self._pymysql.cursors.DictCursor,
            autocommit=True,
        )

    def acquire(self):
        with self._lock:
            if self._available:
                conn = self._available.pop()
                self._used_count += 1
                return conn
            if self._used_count < self._pool_max:
                conn = self._make_conn()
                self._used_count += 1
                return conn
            raise RuntimeError(
                f"MySQL connection pool exhausted "
                f"(max={self._pool_max}, all in use)."
            )
        return None

    def release(self, conn):
        if conn is None:
            return
        with self._lock:
            self._used_count = max(0, self._used_count - 1)
            if len(self._available) < self._pool_max:
                self._available.append(conn)
                return
        try:
            conn.close()
        except Exception:
            pass

    def close_all(self):
        with self._lock:
            conns = self._available[:]
            self._available.clear()
            self._used_count = 0
        for c in conns:
            try:
                c.close()
            except Exception:
                pass

    def ping(self) -> bool:
        conn = None
        try:
            conn = self._make_conn()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            return True
        except Exception as e:
            logger.warning(f"MySQL ping (SELECT 1) failed: {e}")
            return False
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass


def query_mysql(sql: str, params: Optional[List[Any]] = None,
                limit: int = 500) -> Dict[str, Any]:
    conn = None
    try:
        pool = _get_pool()
        conn = pool.acquire()
        with conn.cursor() as cursor:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            rows = cursor.fetchall()
            if isinstance(rows, list):
                rows = rows[:limit]
            affected = getattr(cursor, "rowcount", len(rows))
            return {
                "success": True,
                "row_count": len(rows) if isinstance(rows, list) else 0,
                "affected_rows": affected,
                "columns": list(rows[0].keys()) if rows else [],
                "data": rows,
            }
    except Exception as e:
        logger.error(f"MySQL query failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "sql": sql[:500],
        }
    finally:
        if conn is not None:
            _get_pool().release(conn)


def list_mysql_tables() -> Dict[str, Any]:
    result = query_mysql("SHOW TABLES")
    if result.get("success") and result.get("data"):
        first_key = next(iter(result["data"][0]))
        result["tables"] = [row[first_key] for row in result["data"]]
    return result


def describe_mysql_table(table_name: str) -> Dict[str, Any]:
    safe_name = table_name.replace("`", "").strip()
    if not safe_name:
        return {"success": False, "error": "table_name is empty"}
    return query_mysql(f"DESCRIBE `{safe_name}`")


def init_mysql_pool() -> bool:
    try:
        pool = _get_pool()
        ok = pool.ping()
        if ok:
            logger.info(
                f"MySQL pool initialized: "
                f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB} "
                f"(charset={MYSQL_CHARSET}, "
                f"pool={pool._pool_min}-{pool._pool_max})"
            )
        else:
            logger.warning("MySQL pool init: ping failed, tool will fail at runtime.")
        return ok
    except Exception as e:
        logger.error(f"MySQL pool init error: {e}", exc_info=True)
        return False


def close_mysql_pool():
    global _pool
    if _pool is not None:
        _pool.close_all()
        _pool = None
        logger.info("MySQL pool closed.")