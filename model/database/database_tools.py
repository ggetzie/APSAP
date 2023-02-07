import psycopg2
import environ
import pathlib

SRC_DIR = pathlib.Path(__file__).resolve(strict=True).parent
print(SRC_DIR)
env = environ.Env()

# Store sensitive data and configuration in a file .env
# outside source control
env.read_env(str(SRC_DIR / "../../.env"))

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


def get_pottery_sherd_info(utm_easting, utm_northing, context_num, find_num):
    try:
        conn = psycopg2.connect(**READ_SETTINGS)
        print(
            f"Fetching sherd from database: {utm_easting=}, {utm_northing=}, {context_num=}, {find_num=}"
        )

        cursor = conn.cursor()
        query = """
        SELECT "3d_batch_number", "3d_batch_piece" 
        FROM object.finds
        WHERE
        finds.area_utm_easting_meters=%s  AND
        finds.area_utm_northing_meters=%s AND
        finds.context_number=%s           AND
        finds.find_number=%s;
        """
        cursor.execute(query, (utm_easting, utm_northing, context_num, find_num))
        # Fetch result
        record = cursor.fetchall()
        if len(record) > 1:
            print("Error, detected duplicate entry!")
            return None
        elif len(record) == 0:
            return None, None
        else:
            # print(record, "\n")
            return record[0]

    except (Exception) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cursor.close()
            conn.close()



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


#Adding this function to analyze the relations between the program's result(3d sherd's info) and all the informatioin in

def update_match_info(
    utm_easting, utm_northing, context_num, find_num, new_batch_num, new_sherd_num
):
    try:
        conn = psycopg2.connect(**WRITE_SETTINGS)

        cursor = conn.cursor()

        query_select = """
        SELECT "3d_batch_number", "3d_batch_piece" 
        FROM object.finds
        WHERE
        finds.area_utm_easting_meters=%s  AND
        finds.area_utm_northing_meters=%s AND
        finds.context_number=%s           AND
        finds.find_number=%s;
        """

        query_update = """
        UPDATE object.finds 
        SET "3d_batch_number" = %s, "3d_batch_piece" = %s
        WHERE finds.area_utm_easting_meters = %s and finds.area_utm_northing_meters = %s and finds.context_number = %s and finds.find_number = %s;
        """

        cursor.execute(query_select, (utm_easting, utm_northing, context_num, find_num))
        # Fetch result
        record = cursor.fetchall()
        if len(record) > 1:
            print("Error, detected duplicate entry!")
        else:
            batch_number, sherd_number = record[0]
            if batch_number == new_batch_num and sherd_number == new_sherd_num:
                pass
            else:
                # print("updating...")
                # print(batch_number, batch_number)
                cursor.execute(
                    query_update,
                    (
                        new_batch_num,
                        new_sherd_num,
                        utm_easting,
                        utm_northing,
                        context_num,
                        find_num,
                    ),
                )
                updated_rows = cursor.rowcount
                # print(updated_rows)
                if updated_rows <= 1:
                    conn.commit()

    except (Exception) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            # print("PostgreSQL connection is closed")
 