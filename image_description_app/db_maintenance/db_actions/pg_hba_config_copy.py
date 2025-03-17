import logging
import io
import os
import docker

def configure_pg_hba(db_type, container_name):
    """Настраивает pg_hba.conf."""
    try:
        logging.info(f"Configuring pg_hba.conf for {db_type}...")

        # Генерируем содержимое pg_hba.conf
        hba_content = generate_pg_hba_content(db_type)

        # Записываем содержимое в файл в контейнере
        write_pg_hba_to_container(container_name, hba_content)

        logging.info(f"pg_hba.conf configured successfully for {db_type}.")

    except Exception as e:
        logging.error(f"Error configuring pg_hba.conf: {e}")
        raise

def generate_pg_hba_content(db_type):
    """Генерирует содержимое pg_hba.conf на основе типа БД."""
    #  Примеры правил.  Адаптируйте под свои нужды!
    if db_type == "primary":
        content = """
# Allow local access
local   all             all                                     trust

# Allow connections from the db_maintenance service
host    all             all             0.0.0.0/0           md5

# Allow replication connections from the replica
host    replication     all             0.0.0.0/0           md5
"""
    elif db_type == "replica":
        content = """
# Allow local access
local   all             all                                     trust

# Allow connections from the db_maintenance service
host    all             all             0.0.0.0/0           md5

# Allow replication connections from the primary
host    replication     all             0.0.0.0/0           md5
"""
    else:
        raise ValueError("Invalid database type.")

    return content

def write_pg_hba_to_container(container_name, hba_content):
    """Записывает содержимое в pg_hba.conf в контейнере."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)

        #  Путь к файлу pg_hba.conf внутри контейнера
        hba_path = "/var/lib/postgresql/data/pg_hba.conf"
            #"/etc/postgresql/15/main/pg_hba.conf"

            #"/etc/postgresql/postgresql.conf.d/pg_hba.conf"


        # Создаем объект BytesIO для хранения содержимого файла
        hba_file = io.BytesIO(hba_content.encode('utf-8'))

        # Записываем файл в контейнер (работает как docker cp)
        container.put_archive(os.path.dirname(hba_path), hba_file) # Используем put_archive

        logging.info(f"pg_hba.conf успешно записан в контейнер {container_name}.")

    except docker.errors.NotFound:
        logging.error(f"Контейнер {container_name} не найден.")
        raise
    except docker.errors.APIError as e:
        logging.error(f"Ошибка при работе с Docker API: {e}")
        raise