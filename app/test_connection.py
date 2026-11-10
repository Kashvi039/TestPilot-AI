
from sqlalchemy import text
from app.database import engine

try:
    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        print("Database connected successfully!")

        print("\nPostgreSQL Version:")
        print(result.fetchone()[0])

except Exception as e:
    print("Database connection failed!")
    print("Error:", e)

finally:
    engine.dispose()
