#database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Usa una ruta relativa para la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Imprime la ruta completa del archivo de la base de datos
print(f"Full database path: {os.path.abspath('test.db')}")

# Crea el motor
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Crea la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea la base declarativa
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        print(f"Database Error: {e}")
        db.rollback()
    finally:
        db.close()
