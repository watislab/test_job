import logging
import os
from dotenv import load_dotenv
from . import postgresql_config, pg_hba_config, docker_utils

load_dotenv()

def configure_database(db_type):
    """Настраивает базу данных (Primary или Replica), pg_hba.conf и перезапускает контейнер."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        logging.info(f"Configuring {db_type} database...")
        # Получаем параметры
        if db_type == "primary":
            db_host = os.environ.get("DB_IMAGE_PROCESSING_HOST", "db-image-processing")
            db_port = os.environ.get("POSTGRES_PORT", "5432")
            container_name = os.environ.get("PG_PRIMARY_CONTAINER_NAME", "db-image-processing")
        elif db_type == "replica":
            db_host = os.environ.get("DB_IMAGE_PROCESSING_HOST", "db-image-processing")  # Replica подключается к primary
            db_port = os.environ.get("POSTGRES_PORT", "5432")
            container_name = os.environ.get("PG_REPLICA_CONTAINER_NAME", "db_result_retrieval")
        else:
            logging.error("Invalid database type. Must be 'primary' or 'replica'.")
            return

        db_name = os.environ.get("POSTGRES_DB", "image_processing_db")
        db_user = os.environ.get("POSTGRES_USER", "user")
        db_password = os.environ.get("POSTGRES_PASSWORD", "password")

        # Конфигурируем PostgreSQL
        postgresql_config.configure_postgresql(db_type, db_host, db_port, db_name, db_user, db_password)

        # Конфигурируем pg_hba.conf
        pg_hba_config.configure_pg_hba(db_type, container_name)

        # Перезапускаем контейнер
        docker_utils.restart_db_image_processing(container_name)

    except Exception as e:
        logging.error(f"Error configuring {db_type} database: {e}")
        raise