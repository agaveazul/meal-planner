import sqlite3
from pydantic.v1 import BaseModel
from typing import List
from langchain.tools import Tool
from threading import local

# Thread-local storage for database connections
db_thread_local = local()

def get_db_connection():
    if not hasattr(db_thread_local, "connection"):
        # This ensures that a new connection is created for each thread
        db_path = 'db/recipes.db'
        db_thread_local.connection = sqlite3.connect("db/recipes.db")
    return db_thread_local.connection


def list_tables():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name from sqlite_master WHERE type='table';")
    rows = c.fetchall()
    return "\n".join(row[0] for row in rows if row[0] is not None)

def run_sqlite_query(query):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute(query)
        all = c.fetchall()
        return all
    
    except sqlite3.OperationalError as err:
        return f"The following error occurred: {str(err)}"
        

class RunQueryArgsSchema(BaseModel):
    query: str

run_query_tool = Tool.from_function(
    name="run_sqlite_query",
    description="Run a sqlite query.",
    func=run_sqlite_query,
    args_schema=RunQueryArgsSchema
)

def describe_tables(table_names):
    conn = get_db_connection()
    c = conn.cursor()
    tables = ', '.join("'" + table + "'" for table in table_names)
    rows = c.execute(f"SELECT sql FROM sqlite_master WHERE type='table' and name IN ({tables});")
    response =  '\n'.join(row[0] for row in rows if row[0] is not None)
    print(response)
    return response

class DescribeTablesArgsSchema(BaseModel):
    table_names: List[str]

describe_tables_tool = Tool.from_function(
    name="describe_tables",
    description="Given a list of table names, returns the schema of those tables",
    func=describe_tables,
    args_schema=DescribeTablesArgsSchema
)