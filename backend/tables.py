from sqlalchemy import create_engine, inspect
import os

# Define the database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Create the engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create inspector from engine
inspector = inspect(engine)

# Print columns of each table
def show_table_details():
    tables = inspector.get_table_names()
    if not tables:
        print("No tables found in the database.")
    else:
        for table_name in tables:
            print(f"\n📦 Table: {table_name}")
            columns = inspector.get_columns(table_name)
            for column in columns:
                col_name = column['name']
                col_type = column['type']
                nullable = column['nullable']
                default = column['default']
                print(f"  - {col_name} ({col_type}) | Nullable: {nullable} | Default: {default}")

if __name__ == "__main__":
    show_table_details()
