from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from pathlib import Path

# Use absolute path so .env is found regardless of working directory
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / '.env')

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Check your .env file.")

engine = create_engine(DATABASE_URL)