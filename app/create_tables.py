
from app.database import engine, Base
from app import models

def create_tables():

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully!")

    print("Tables:", Base.metadata.tables.keys())


if __name__ == "__main__":
    create_tables()
