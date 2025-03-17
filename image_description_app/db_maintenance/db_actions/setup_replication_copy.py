import logging
import os
import psycopg2
import docker
from dotenv import load_dotenv

load_dotenv()

def configure_database(db_type):
    """Настраивает базу данных (Primary или Replica) используя ALTER SYSTEM и перезапускает контейнер."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        logging.info(f"Configuring {db_type} database using ALTER SYSTEM...")
        # Определяем параметры подключения
        if db_type == "primary":
            db_host = os.environ.get("DB_IMAGE_PROCESSING_HOST", "db-image-processing")
            db_port = os.environ.get("POSTGRES_PORT", "5432")
            container_name = os.environ.get("PG_PRIMARY_CONTAINER_NAME", "db-image-processing")
        elif db_type == "replica":
            db_host = os.environ.get("DB_IMAGE_PROCESSING_HOST", "db-image-processing")  # Replica подключается к primary
            db_port = os.environ.get("POSTGRES_PORT", "5432")
            container_name = os.environ.get("PG_REPLICA_CONTAINER_NAME", "db-result-retrieval")
        else:
            logging.error("Invalid database type. Must be 'primary' or 'replica'.")
            return

        db_name = os.environ.get("POSTGRES_DB", "image_processing_db")
        db_user = os.environ.get("POSTGRES_USER", "user")
        db_password = os.environ.get("POSTGRES_PASSWORD", "password")

        # Подключаемся к ЦЕЛЕВОЙ базе данных
        conn = psycopg2.connect(host=db_host, port=db_port, database=db_name, user=db_user, password=db_password)
        conn.autocommit = True  # Выполняем коммиты сразу

        with conn.cursor() as cur:
            # Определяем параметры конфигурации в зависимости от типа БД
            if db_type == "primary":
                # Настройки для Primary
                primary_conninfo = ""
                hot_standby = "off"
                wal_level = "replica"
                synchronous_commit = "off"
                max_wal_senders = "5"
                synchronous_standby_names = "''"  # Пустая строка для primary
                archive_mode = "on"
                archive_command = "cp /var/lib/postgresql/data/pg_wal/%p /path/to/archive/%f"
            elif db_type == "replica":
                primary_conninfo = f"host=db-image-processing port={db_port} user={db_user} password={db_password} application_name=db-result-retrieval"  # Replica подключается к primary
                hot_standby = "on"
                wal_level = "replica"
                synchronous_commit = "on"
                max_wal_senders = "5"
                synchronous_standby_names = "'db-result-retrieval'"  # Имя replica
                archive_mode = "off"
                archive_command = ""
            else:
                logging.error("Invalid database type. Must be 'primary' or 'replica'.")
                return

            # Выполняем ALTER SYSTEM для каждого параметра
            cur.execute(f"ALTER SYSTEM SET primary_conninfo = '{primary_conninfo}';")
            cur.execute(f"ALTER SYSTEM SET hot_standby = '{hot_standby}';")
            cur.execute(f"ALTER SYSTEM SET wal_level = '{wal_level}';")
            cur.execute(f"ALTER SYSTEM SET synchronous_commit = '{synchronous_commit}';")
            cur.execute(f"ALTER SYSTEM SET max_wal_senders = '{max_wal_senders}';")
            cur.execute(f"ALTER SYSTEM SET synchronous_standby_names = {synchronous_standby_names};")
            cur.execute(f"ALTER SYSTEM SET archive_mode = '{archive_mode}';")
            cur.execute(f"ALTER SYSTEM SET archive_command = '{archive_command}';")
            cur.execute("ALTER SYSTEM SET listen_addresses = '*';")

        logging.info(f"{db_type} database configured successfully using ALTER SYSTEM.")

        # Перезапускаем контейнер
        restart_db_image_processing(container_name)

    except psycopg2.Error as e:
        logging.error(f"Error configuring {db_type} database: {e}")
        raise
    except Exception as e:
        logging.error(f"Error configuring {db_type} database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def restart_db_image_processing(container_name):
    """Перезапускает контейнер."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        container.restart()
        logging.info(f"Контейнер {container_name} успешно перезапущен.")

    except docker.errors.NotFound:
        logging.error(f"Контейнер {container_name} не найден.")
    except docker.errors.APIError as e:
        logging.error(f"Ошибка при работе с Docker API: {e}")