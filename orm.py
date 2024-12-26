import sqlite3
import inspect

class Database:
    def __init__(self, path) -> None:
        self.conn = sqlite3.Connection(path)

    @property
    def tables(self):
        SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"
        return [x[0] for x in self.conn.execute(SELECT_TABLES_SQL).fetchall()]
    

    def create(self, table):
        self.conn.execute(table._get_create_sql())
    

class Table:

    @classmethod
    def _get_create_sql(cls):

        SQL_STATEMENT = "CREATE TABLE IF NOT EXISTS {name} ({columns});"

        table_name = cls.__name__.lower()
        
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT", ]
        for name ,obj in inspect.getmembers(cls):
            if isinstance(obj, Column):
                columns.append(f"{name} {obj.sql_type}")
            elif isinstance(obj, ForeignKey):
                columns.append(f"{name}_id INTEGER")
        columns_str = ", ".join(columns)

        return SQL_STATEMENT.format(name=table_name, columns=columns_str)


class Column:
    def __init__(self, column_type) -> None:
        self.type = column_type

    @property
    def sql_type(self):
        SQLITE_TYPE_MAP = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bytes: "BLOB",
            bool: "INTEGER",  # 0 or 1
        }
        return SQLITE_TYPE_MAP[self.type]

class ForeignKey:
    def __init__(self, table) -> None:
        self.table = table