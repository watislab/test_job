import asyncio
import logging
import sys

from config.logging_config import setup_logging
from .db_actions.setup_replication import configure_database
from .alembic_operations.migrations import run_migrations
from dotenv import load_dotenv

load_dotenv()

async def main():
    """Точка входа, выбор действия."""
    setup_logging()
    action = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        if action == "setup_primary":
            configure_database("primary")
            logging.info("Initial database setup completed.")
        elif action == "setup_replica":
            configure_database("replica")
            logging.info("Initial database setup completed.")
        elif action == "run_migrations":
            run_migrations()
            logging.info("Migrations run completed.")
        else:
            logging.error("Invalid action. Available actions: setup_primary, setup_replica, run_migrations")
    except Exception as e:
        logging.error(f"Action failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())