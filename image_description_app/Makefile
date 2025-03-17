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

# up-build:
# 	$(SUDO) docker compose -f $(COMPOSE_FILE) up -d --build --remove-orphans

stop:
	$(SUDO) docker compose -f $(COMPOSE_FILE) stop

down:
	$(SUDO) docker compose -f $(COMPOSE_FILE) down

# Очистка образов db_maintenance перед up-build
before-up-build:
	@echo "Checking for images ending with $(SERVICE_NAME)"

	@sudo docker images | grep "$(SERVICE_NAME)" | awk '{print $$3}' | xargs -r sudo docker rmi -f

# Цели для запуска Alembic
pg-primary-setup:
	$(SUDO) docker compose -f $(COMPOSE_FILE) --profile db_maintenance_tasks run --rm $(SERVICE_NAME) $(PYTHON_COMMAND) setup_primary --no-cache

pg-replica-setup:
	$(SUDO) docker compose -f $(COMPOSE_FILE) --profile db_maintenance_tasks run --rm  $(SERVICE_NAME) $(PYTHON_COMMAND) setup_replica --no-cache

migrate-primary:
	$(SUDO) docker compose -f $(COMPOSE_FILE) --profile db_maintenance_tasks run --rm $(SERVICE_NAME) $(PYTHON_COMMAND) run_migrations

# Переопределяем up-build, чтобы сначала чистить образы
up-build: before-up-build
	$(SUDO) docker compose -f $(COMPOSE_FILE) up -d --build --remove-orphans