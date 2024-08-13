#create_tables.py
import sys
import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Add the root directory of the project to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SQLALCHEMY_DATABASE_URL
from models import Base, User, Group, GroupMember, Keyword, Post, Reaction, Comment, Friendship, Notification

def create_tables(recreate=False):
    try:
        # Print the SQLite version
        print(f"SQLite version: {sqlite3.sqlite_version}")

        # Print the database URL
        print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

        # Check if the database file exists
        db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
        print(f"Database file path: {db_path}")

        # Ensure the directory exists
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)
        print(f"Database directory created/checked: {db_dir}")

        print(f"Database file exists: {os.path.exists(db_path)}")
        print(f"Directory writable: {os.access(db_dir, os.W_OK)}")

        if recreate:
            Base.metadata.drop_all(bind=engine)
            print("Existing tables dropped")

        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")
    except SQLAlchemyError as e:
        print(f"An SQLAlchemy error occurred while creating tables: {e}")
        print(f"Error type: {type(e).__name__}")
    except Exception as e:
        print(f"An unexpected error occurred while creating tables: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    create_tables(recreate=True)  # Set to False if you don't want to drop existing tables
