from sqlmodel import Session, create_engine, SQLModel
from . import models
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

sqlite_file = DATA_DIR / "study_mate.db"

sqlite_url = f"sqlite:///{sqlite_file}"


engine = create_engine(
    sqlite_url,
    connect_args={
        "check_same_thread": False
    }
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

        
if __name__ == "__main__":
    create_db_and_tables()