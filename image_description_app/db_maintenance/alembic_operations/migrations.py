import logging
import os
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    """Применяет миграции."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    alembic_ini_path = os.path.join(os.path.dirname(__file__), "../../result_retrieval_service/migrations/alembic.ini") # Define where file is
    config = Config(alembic_ini_path)
    alembic_db_url = os.environ.get("DATABASE_URL") # Reading the url with envs
    if alembic_db_url is not None: # Dynamic database change
        config.set_main_option("sqlalchemy.url", alembic_db_url)

    try:
        command.upgrade(config, "head")
        logging.info("Migrations applied successfully.")
    except Exception as e:
        logging.error(f"Error applying migrations: {e}")
        raise