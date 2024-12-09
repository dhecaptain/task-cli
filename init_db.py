from database import create_table, create_indexes

if __name__ == "__main__":
    print("Initializing database...")
    create_table()
    create_indexes()
    print("Database initialized successfully!")
