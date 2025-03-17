# pg_hba_config.py

import logging
import io
import os
import docker
import tarfile

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
host    replication     all             all             0.0.0.0/0           md5
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
        hba_path = "/var/lib/postgresql/data/pg_hba.conf"  #  Проверьте правильность пути!

        # Создаем tar-архив в памяти
        hba_file = io.BytesIO()
        with tarfile.open(fileobj=hba_file, mode='w:tar') as tar:
            # Создаем TarInfo объект для файла pg_hba.conf
            tarinfo = tarfile.TarInfo(os.path.basename(hba_path))
            tarinfo.size = len(hba_content.encode('utf-8'))  # Указываем размер файла
            # Записываем содержимое файла в архив
            tar.addfile(tarinfo, io.BytesIO(hba_content.encode('utf-8')))

        # Перемещаем указатель в начало файла
        hba_file.seek(0)

        # Записываем архив в контейнер
        container.put_archive(os.path.dirname(hba_path), hba_file)  # Используем put_archive

        logging.info(f"pg_hba.conf успешно записан в контейнер {container_name}.")

    except docker.errors.NotFound:
        logging.error(f"Контейнер {container_name} не найден.")
        raise
    except docker.errors.APIError as e:
        logging.error(f"Ошибка при работе с Docker API: {e}")
        raise