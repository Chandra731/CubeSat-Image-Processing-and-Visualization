from sqlalchemy import create_engine, MetaData, Table, select, desc, asc
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Set up SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
metadata = MetaData()
metadata.reflect(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

def get_table(name):
    return Table(name, metadata, autoload_with=engine)

def display_table(table_name, sort_by=None, descending=False):
    table = get_table(table_name)
    stmt = select(table)
    if sort_by:
        stmt = stmt.order_by(desc(table.c[sort_by]) if descending else asc(table.c[sort_by]))
    result = session.execute(stmt).fetchall()
    print("\n" + tabulate(result, headers=table.columns.keys(), tablefmt="grid"))

def add_row(table_name):
    table = get_table(table_name)
    print("\nEnter values for the new row:")
    data = {}
    for col in table.columns:
        if col.name == 'id':  # auto-increment primary key
            continue
        val = input(f"{col.name} ({col.type}): ")
        if val == "" and col.nullable:
            val = None
        data[col.name] = val
    ins = table.insert().values(**data)
    session.execute(ins)
    session.commit()
    print("[+] Row added successfully.")

def delete_row(table_name):
    table = get_table(table_name)
    row_id = input("Enter the ID of the row to delete: ")
    stmt = table.delete().where(table.c.id == row_id)
    result = session.execute(stmt)
    session.commit()
    print(f"[x] {result.rowcount} row(s) deleted.")

def sort_table(table_name):
    table = get_table(table_name)
    columns = list(table.columns.keys())
    print("\nSortable columns:")
    for i, col in enumerate(columns):
        print(f"{i + 1}. {col}")
    choice = int(input("Choose column number to sort by: ")) - 1
    direction = input("Sort descending? (y/N): ").lower().startswith("y")
    display_table(table_name, sort_by=columns[choice], descending=direction)

def menu():
    table_names = list(metadata.tables.keys())
    while True:
        print("\n Available Tables:")
        for idx, name in enumerate(table_names, 1):
            print(f"{idx}. {name}")
        print("0. Exit")

        choice = input("Select a table (0 to exit): ")
        if choice == "0":
            break
        elif not choice.isdigit() or int(choice) not in range(1, len(table_names)+1):
            print("Invalid choice.")
            continue

        selected_table = table_names[int(choice) - 1]

        while True:
            print(f"\n Managing Table: {selected_table}")
            print("1. View Data")
            print("2. Add Row")
            print("3. Delete Row by ID")
            print("4. Sort and View")
            print("0. Back")

            action = input("Choose an action: ")
            if action == "1":
                display_table(selected_table)
            elif action == "2":
                add_row(selected_table)
            elif action == "3":
                delete_row(selected_table)
            elif action == "4":
                sort_table(selected_table)
            elif action == "0":
                break
            else:
                print("Invalid action.")

if __name__ == "__main__":
    menu()
