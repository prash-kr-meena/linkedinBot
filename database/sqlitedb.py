import sqlite3
import json
import logging
from enum import Enum, unique
from typing import Union, TypeVar, Iterable, Generator

try:
    import database_logger
    dblogger = logging.getLogger(database_logger.DBLOGGER_NAME)
    logging.basicConfig(level=logging.DEBUG)
except:
    dblogger = logging.getLogger("database")
    logging.basicConfig(level=logging.DEBUG)

# Defines type hint for row set result of an SQL/DQL query returned by DB API.
# A successful call returns a list of tuples, with each tuple holding values
# for a single row. An empty row set corresponds to an empty list. Also,
# a bare None is added to the definition, which can be returned to indicate
# an exception.
TScalar = TypeVar('TScalar', str, float, int, bool, None)
TRow = Iterable[TScalar]
TRowSet = Iterable[TRow]

#
TSQLiteDB = TypeVar("TSQLiteDB", bound="SQLiteDB")

WITH_WRAPPER = """
WITH rowset AS (
    {query}
)
SELECT json_group_array(json_array(
    {columns}
    )) AS json_rowset
FROM rowset;
"""

DB_META_SQL = {
    "main_path": "SELECT file FROM pragma_database_list() WHERE name = 'main';"
}


@unique
class TransactionType(Enum):
    DEFAULT = None
    DEFERRED = "DEFERRED"
    IMMEDIATE = "IMMEDIATE"
    EXCLUSIVE = "EXCLUSIVE"


class SQLiteDB:
    """SQLite database manager. Manages SQLite connection

    Attributes:
      path: Resolved database path reported by the engine.
      uri: Path or URI string describing the main database.
      con: Connection instance.
      cur: Cursor instance.
      txn_type: Implicit transaction type (property).
        If set to TransactionType.DEFAULT, implicit transactions are disabled.

    TODO: Add integrity checking routine (see 'SQLiteC for VBA').
    """

    path: str
    uri: str
    con: Union[sqlite3.Connection, None]
    cur: Union[sqlite3.Cursor, None]
    txn_type: TransactionType

    def __init__(self, uri: str = None) -> None:
        if uri is None:
            self.uri = ":memory:"
        else:
            self.uri = uri
        self.path = ""
        self.con = None
        self.cur = None
        print(f"Created DB Connection - {uri}")

    def __del__(self):
        """Closes the sqlite3.Cursor and sqlite3.Connection objects before destruction."""
        print("\n\nClosing DB Connection!!")
        self.close()

    def __repr__(self) -> str:
        return f"<sqlitedb.SQLiteDB instance. Main DB - {self.path}>"

    def __str__(self) -> str:
        return self.__repr__()

    def _get_txn_type(self):
        if self.con is not None:
            return TransactionType.__getitem__(self.con.isolation_level or "DEFAULT")

    def _set_txn_type(self, txn_type: TransactionType):
        self.con.isolation_level = txn_type.value

    txn_type = property(fget=_get_txn_type, fset=_set_txn_type, fdel=None,
                        doc="SQLite transaction type (None/DEFERRED/IMMEDIATE/EXCLUSIVE).")

    def open(self, txn_type: TransactionType = TransactionType.DEFERRED,
             row_factory: type(sqlite3.Row) = None) -> TSQLiteDB:

        """Opens a database connection (if not previously opened)."""
        if self.con is not None:
            raise sqlite3.OperationalError('Connection already open!')

        is_uri: bool = self.uri[0:5].lower() == "file:"
        try:  # Open database connection, get cursor
            self.con = sqlite3.connect(self.uri, isolation_level=txn_type.value, uri=is_uri)
            self.path = self.con.cursor().execute(DB_META_SQL["main_path"]).fetchone()[0]
            self.cur = self.con.cursor()
        except sqlite3.OperationalError as err:
            dblogger.exception(err.args[0])
            raise
        except sqlite3.Error as err:
            dblogger.exception(f"Unexpected {err=}, {type(err)=}")
            raise

        self.con.row_factory = row_factory
        return self

    def close(self) -> None:
        if self.con is None:
            return

        self.cur.close()
        self.cur = None

        self.con.close()
        self.con = None

    def begin(self, txn_type: TransactionType = TransactionType.DEFAULT) -> None:
        if txn_type.value is not None:
            self.con.isolation_level = None
            query = f"BEGIN {txn_type.value};"
        else:
            query = "BEGIN;"
        self.execute_nonquery(query)

    def commit(self) -> None:
        self.execute_nonquery("COMMIT;")

    def savepoint(self, name: str) -> None:
        if len(name) == 0:
            raise ValueError("SAVEPOINT name cannot be blank.")
        self.execute_nonquery(f"SAVEPOINT {name};")

    def release(self, name: str) -> None:
        if len(name) == 0:
            raise ValueError("RELEASE name cannot be blank.")
        self.execute_nonquery(f"RELEASE {name};")

    def rollback(self, name: str = None) -> None:
        if name is None or len(name) == 0:
            query = "ROLLBACK;"
        else:
            query = f"ROLLBACK TO {name};"
        self.execute_nonquery(query)

    def column_names(self, query: str = None) -> tuple[str, ...]:
        """Retrieves the list of column names returned by the query"""
        meta = self.prepare_and_execute(query).description
        return tuple(row[0] for idx, row in enumerate(meta))

    def rowset2json(self, query: str) -> str:
        """Wraps SELECT query in WITH and collapses rowset to JSON object."""
        columns = str(self.column_names(query)).replace("'", '"')[1:-1]
        # The column_names function returns a tuple; remove the terminal comma
        # from a 1-tuple for a single returned column.
        if columns[-1:] == ",":
            columns = columns[:-1]
        return WITH_WRAPPER.format(
            query=query.strip(" \n;").replace("\n", "\n" + " " * 4),
            columns=columns
        )

    def prepare_and_execute(
            self,
            query: str = None,
            query_params: Union[tuple, dict] = (),
            page_size: int = None,
            is_script: bool = False
    ) -> sqlite3.Cursor:
        """Executes query and prepares cursor/statement

        If blank query is provided and the cursor is 'prepared', simply return
        the cursor. This logic is useful for calling methods requiring a prepared
        cursor, but which should used currently prepared cursor, if available,
        when no query is provided.
        """
        if query is None or len(query) == 0:
            if self.cur is None or self.cur.description is None:
                raise ValueError("query must be provided to unprepared cursor.")
            return self.cur

        if not (page_size is None or isinstance(page_size, int)):
            raise TypeError("page_size must be an int or None.")

        if self.cur is None:
            self.open()

        if page_size is not None:
            self.cur.arraysize = page_size

        dblogger.debug(f"Query: {query}")

        try:
            if not is_script:
                if not isinstance(query_params, list):
                    cur = self.cur.execute(query, query_params)
                else:
                    cur = self.cur.executemany(query, query_params)
            else:
                cur = self.cur.executescript(query)
        except sqlite3.DatabaseError as err:
            dblogger.exception(str(err))
            raise
        return cur

    def execute_nonquery(self, query: str, query_params: Union[tuple, dict] = ()) -> int:
        """Executes a DML/DDL statement and returns the 'changes' count."""
        accrued_changes = self.con.total_changes
        self.prepare_and_execute(query, query_params)
        return self.con.total_changes - accrued_changes

    def execute_script(self, query: str) -> int:
        """Executes multiple DML/DDL statements and returns the 'changes' count."""
        accrued_changes = self.con.total_changes
        self.prepare_and_execute(query, is_script=True)
        return self.con.total_changes - accrued_changes

    def fetch_scalar(self, query: str, query_params: Union[tuple, dict] = ()) -> TScalar:
        """Fetches a scalar value from database."""
        return self.prepare_and_execute(query, query_params).fetchone()[0]

    def fetch_rowset(self, query: str, query_params: Union[tuple, dict] = ()) -> TRowSet:
        """Fetches all rows returned by the query."""
        return self.prepare_and_execute(query, query_params).fetchall()

    def fetch_json_rowset(self, query: str, query_params: Union[tuple, dict] = ()) -> TRowSet:
        """Fetches all rows returned by the query via a JSON container.

        Wraps supplied query in WITH and packs rowset yielded by the original
        query to a JSON object on the engine side. This JSON-packed rowset is
        fetched as a single string value and decoded into list of lists via the
        json module.
        """
        return json.loads(
            self.prepare_and_execute(self.rowset2json(query), query_params).fetchone()[0]
        )

    def fetch_page(self, query: str = None, query_params: Union[tuple, dict] = (),
                   page_size: int = None) -> TRowSet:
        """Fetches a page of rows.

        To retrieve the first page, provide a valid query and, optionally, page
        size (if provided, the associated parameter is updated). For subsequent
        pages, call this method with no arguments.
        """
        return self.prepare_and_execute(query, query_params=query_params, page_size=page_size).fetchmany()

    def fetch_page_gen(self, query: str, query_params: Union[tuple, dict] = (),
                       page_size: int = None) -> Generator[list[tuple], None, None]:
        """Fetches a page of rows.

        To retrieve the first page, provide a valid query and, optionally, page
        size (if provided, the associated parameter is updated). For subsequent
        pages, call this method with no arguments.
        """
        self.prepare_and_execute(query, query_params=query_params, page_size=page_size)
        page = self.cur.fetchmany()
        while len(page) > 0:
            yield page
            page = self.cur.fetchmany()
        yield page
