"""
Migration script to clear old memory game data and recreate tables with UUID user IDs.
Run this script after updating the code to use UUIDs.
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load database connection details
load_dotenv()

# Database connection
DB_HOST = os.getenv("DB_HOST", "bigcasino-memory_db-1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "memory_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def clear_and_recreate_tables():
    """Drop existing tables and let them be recreated with new UUID schema"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = False
        
        print("Connected to database successfully")
        
        # Drop existing tables
        with conn.cursor() as cursor:
            print("Dropping existing tables...")
            cursor.execute("DROP TABLE IF EXISTS games CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS cards CASCADE;")
            conn.commit()
            print("Tables dropped successfully")
        
        conn.close()
        print("Database connection closed")
        print("\n✅ Migration completed successfully!")
        print("Please restart the memory services:")
        print("  - docker restart bigcasino-memory-1")
        print("  - docker restart bigcasino-memory_logic-1")
        print("  - docker restart bigcasino-memory_adapter-1")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clear_and_recreate_tables()
