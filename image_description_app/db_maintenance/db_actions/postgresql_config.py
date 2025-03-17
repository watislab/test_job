import logging
import psycopg2

def configure_postgresql(db_type, db_host, db_port, db_name, db_user, db_password):
    """Настраивает PostgreSQL (ALTER SYSTEM)."""
    try:
        logging.info(f"Configuring PostgreSQL (ALTER SYSTEM) for {db_type}...")
        conn = psycopg2.connect(host=db_host, port=db_port, database=db_name, user=db_user, password=db_password)
        conn.autocommit = True

        with conn.cursor() as cur:
            if db_type == "primary":
                primary_conninfo = ""
                hot_standby = "off"
                wal_level = "replica"
                synchronous_commit = "off"
                max_wal_senders = "5"
                synchronous_standby_names = "''"
                archive_mode = "on"
                archive_command = "cp /var/lib/postgresql/data/pg_wal/%p /path/to/archive/%f"
            elif db_type == "replica":
                primary_conninfo = f"host={db_host} port={db_port} user={db_user} password={db_password} application_name=db_result_retrieval"
                hot_standby = "on"
                wal_level = "replica"
                synchronous_commit = "on"
                max_wal_senders = "5"
                synchronous_standby_names = "'db_result_retrieval'"
                archive_mode = "off"
                archive_command = ""
            else:
                raise ValueError("Invalid database type.")

            cur.execute(f"ALTER SYSTEM SET primary_conninfo = '{primary_conninfo}';")
            cur.execute(f"ALTER SYSTEM SET hot_standby = '{hot_standby}';")
            cur.execute(f"ALTER SYSTEM SET wal_level = '{wal_level}';")
            cur.execute(f"ALTER SYSTEM SET synchronous_commit = '{synchronous_commit}';")
            cur.execute(f"ALTER SYSTEM SET max_wal_senders = '{max_wal_senders}';")
            cur.execute(f"ALTER SYSTEM SET synchronous_standby_names = {synchronous_standby_names};")
            cur.execute(f"ALTER SYSTEM SET archive_mode = '{archive_mode}';")
            cur.execute(f"ALTER SYSTEM SET archive_command = '{archive_command}';")
            cur.execute("ALTER SYSTEM SET listen_addresses = '*';")

        logging.info(f"PostgreSQL (ALTER SYSTEM) configured successfully for {db_type}.")

    except psycopg2.Error as e:
        logging.error(f"Error configuring PostgreSQL: {e}")
        raise
    finally:
        if conn:
            conn.close()