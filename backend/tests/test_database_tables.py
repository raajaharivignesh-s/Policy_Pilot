from sqlalchemy import inspect

from app.database.connection import engine


def test_database_tables():
    inspector = inspect(engine)

    tables = inspector.get_table_names()

    print("\n========================================")
    print("DATABASE TABLES")
    print("========================================")

    for table in tables:
        print(f"- {table}")

    expected_tables = {
        "users",
        "citizen_profiles",
        "conversations",
        "messages",
        "agent_executions",
        "schemes",
        "feedback",
    }

    assert expected_tables.issubset(set(tables))