import logging
import os
import subprocess
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def configure_database(db_type):
    """Настраивает базу данных (Primary или Replica) используя ALTER SYSTEM и изменяет pg_hba.conf."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        logging.info(f"Configuring {db_type} database using ALTER SYSTEM...")
        # Определяем параметры подключения из переменных окружения
        db_host = os.environ.get("DB_IMAGE_PROCESSING_HOST", "db-image-processing")
        db_name = os.environ.get("POSTGRES_DB", "image_processing_db")
        db_user = os.environ.get("POSTGRES_USER", "user")
        db_password = os.environ.get("POSTGRES_PASSWORD", "password")

        # Подключаемся к базе данных
        conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
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
                synchronous_standby_names = ""
                archive_mode = "on"
                archive_command = "cp /var/lib/postgresql/data/pg_wal/%p /path/to/archive/%f"
            elif db_type == "replica":
                primary_conninfo = f"host={db_host} port=5432 user={db_user} password={db_password} application_name=result-retrieval-db"
                hot_standby = "on"
                wal_level = "replica"
                synchronous_commit = "on"
                max_wal_senders = "5"
                synchronous_standby_names = "'db-result-retrieval'"
                archive_mode = "off"
                archive_command = ""
            else:
                logging.error("Invalid database type. Must be 'primary' or 'replica'.")
                return

            #  Выполняем ALTER SYSTEM для каждого параметра
            cur.execute(f"ALTER SYSTEM SET primary_conninfo = '{primary_conninfo}';")
            cur.execute(f"ALTER SYSTEM SET hot_standby = '{hot_standby}';")
            cur.execute(f"ALTER SYSTEM SET wal_level = '{wal_level}';")
            cur.execute(f"ALTER SYSTEM SET synchronous_commit = '{synchronous_commit}';")
            cur.execute(f"ALTER SYSTEM SET max_wal_senders = '{max_wal_senders}';")
            cur.execute(f"ALTER SYSTEM SET synchronous_standby_names = {synchronous_standby_names};")
            cur.execute(f"ALTER SYSTEM SET archive_mode = '{archive_mode}';")
            cur.execute(f"ALTER SYSTEM SET archive_command = '{archive_command}';")
            cur.execute("ALTER SYSTEM SET listen_addresses = '*';")

        #  Настраиваем pg_hba.conf
        configure_pg_hba(db_type)  # Configure hba
        #  Перезагружаем конфигурацию
        subprocess.run(["pg_ctl", "-D", "/var/lib/postgresql/data", "reload"], check=True, capture_output=True)
        logging.info(f"{db_type} database configured successfully using ALTER SYSTEM.")

    except psycopg2.Error as e:
        logging.error(f"Error configuring {db_type} database: {e}")
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"Error reloading configuration: {e.stderr.decode()}")
        raise
    except Exception as e:
        logging.error(f"Error configuring {db_type} database: {e}")
        raise
    finally:
        if conn:
            conn.close()


def configure_pg_hba(db_type):
    """Настраивает pg_hba.conf для доступа из сети Docker."""
    pg_hba_path = "/etc/postgresql/pg_hba.conf"
    docker_network_rule = "host  all  all  0.0.0.0/0  trust\n" # Docker network access
    local_connection_rule = "local   all             all                                     trust\n"

    try:
        # Проверяем, существует ли файл
        if not os.path.exists(pg_hba_path):
            logging.error(f"pg_hba.conf not found at {pg_hba_path}")
            return

        with open(pg_hba_path, "r") as f:
            pg_hba_content = f.readlines()

        # Добавляем правило для локального подключения, если его нет
        if local_connection_rule not in pg_hba_content:
            pg_hba_content.insert(0, local_connection_rule)  # Insert at the beginning
            logging.info("Added rule for local connection to pg_hba.conf")

        # Добавляем правило для сети Docker, если его нет
        if docker_network_rule not in pg_hba_content:
            pg_hba_content.append(docker_network_rule)
            logging.info("Added rule for Docker network access to pg_hba.conf")

        # Записываем изменения обратно в файл
        with open(pg_hba_path, "w") as f:
            f.writelines(pg_hba_content)

        logging.info("pg_hba.conf configured successfully.")

    except Exception as e:
        logging.error(f"Error configuring pg_hba.conf: {e}")
        raise