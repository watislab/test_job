# Проверяем, нужен ли sudo для docker
ifneq (,$(shell which sudo))
  SUDO := sudo
else
  SUDO :=
endif

# Общие переменные
COMPOSE_FILE := docker-compose.yaml
SERVICE_NAME := db_maintenance
PYTHON_COMMAND := python -m main

# Цели для управления Docker Compose
build:
	$(SUDO) docker compose -f $(COMPOSE_FILE) build

up-build:
	$(SUDO) docker compose -f $(COMPOSE_FILE) up -d --build --remove-orphans

stop:
	$(SUDO) docker compose -f $(COMPOSE_FILE) stop

down:
	$(SUDO) docker compose -f $(COMPOSE_FILE) down

# Цели для запуска Alembic
pg-primary-setup:
	$(SUDO) docker compose -f $(COMPOSE_FILE) run $(SERVICE_NAME) $(PYTHON_COMMAND) setup_primary --no-cache

pg-replica-setup:
	$(SUDO) docker compose -f $(COMPOSE_FILE) run $(SERVICE_NAME) $(PYTHON_COMMAND) setup_replica

migrate-primary:
	$(SUDO) docker compose -f $(COMPOSE_FILE) run $(SERVICE_NAME) $(PYTHON_COMMAND) run_migrations