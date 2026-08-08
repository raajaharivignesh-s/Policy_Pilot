from app.database.base import Base
from app.database.connection import engine

# Import all models so SQLAlchemy registers them
# with Base.metadata.
from app import models  # noqa: F401


def init_database() -> None:
    """
    Create all PostgreSQL tables defined by the SQLAlchemy models.
    """

    Base.metadata.create_all(
        bind=engine,
    )


if __name__ == "__main__":
    init_database()
    print("Database tables created successfully.")