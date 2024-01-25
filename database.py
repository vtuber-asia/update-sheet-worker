from os import getenv
from peewee import SqliteDatabase, MySQLDatabase, PostgresqlDatabase
from errors import UndefinedDatabaseConnectionType


def connect_db():
    connection_type = getenv('DB_TYPE')
    database_name = getenv('DB_NAME')
    if connection_type == "sqlite":
        return SqliteDatabase(database_name)
    if connection_type == "mysql":
        return MySQLDatabase(
            database_name,
            user=getenv('DB_USER'),
            password=getenv('DB_PASS'),
            host=getenv('DB_HOST'),
            port=int(getenv('DB_PORT'))
        )
    if connection_type == "postgres":
        return PostgresqlDatabase(
            database_name,
            user=getenv('DB_USER'),
            password=getenv('DB_PASS'),
            host=getenv('DB_HOST'),
            port=getenv('DB_PORT')
        )
    raise UndefinedDatabaseConnectionType


db = connect_db()
