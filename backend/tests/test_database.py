from sqlalchemy import text

from app.database.connection import engine


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    assert value == 1