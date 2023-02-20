import psycopg2
import environ
import pathlib

SRC_DIR = pathlib.Path(__file__).resolve(strict=True).parent
 
env = environ.Env()

# Store sensitive data and configuration in a file .env
# outside source control
env.read_env(str(SRC_DIR / "../.env"))

READ_SETTINGS = {
    "database": env("DB_NAME"),
    "host": env("DB_HOST"),
    "user": env("DB_READ_USER"),
    "password": env("DB_READ_PW"),
    "port": env("DB_PORT"),
    "sslmode": env("DB_SSL_MODE"),
}

WRITE_SETTINGS = {
    "database": env("DB_NAME"),
    "host": env("DB_HOST"),
    "user": env("DB_WRITE_USER"),
    "password": env("DB_WRITE_PW"),
    "port": env("DB_PORT"),
    "sslmode": env("DB_SSL_MODE"),
}

 


def get_all_pottery_sherd_info():
    try:
        conn = psycopg2.connect(**READ_SETTINGS)
        print(
            f"Fetching all sherds from database"
        )

        cursor = conn.cursor()
        query = """
        SELECT *
        FROM object.finds
        """
        print("Started query")
        cursor.execute(query)
        print("Ended query")
        # Fetch result
        records = cursor.fetchall()
        return records

    except (Exception) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cursor.close()
            conn.close()

