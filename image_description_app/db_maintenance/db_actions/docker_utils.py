import logging
import docker

def restart_db_image_processing(container_name):
    """Перезапускает контейнер."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        container.restart()
        logging.info(f"Контейнер {container_name} успешно перезапущен.")

    except docker.errors.NotFound:
        logging.error(f"Контейнер {container_name} не найден.")
        raise
    except docker.errors.APIError as e:
        logging.error(f"Ошибка при работе с Docker API: {e}")
        raise