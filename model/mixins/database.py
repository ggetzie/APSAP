from pathlib import Path
import logging

import psycopg2
import environ

SRC_DIR = Path(__file__).resolve(strict=True).parent


# Store sensitive data and configuration in a file .env
# outside source control
env = environ.Env()
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


class DatabaseMixin:
    def __init__(self):
        """This constructor initializes a database connection that gets reused throughout the whole application"""
        self.conn = psycopg2.connect(**READ_SETTINGS)

    def get_sherd_info(self, utm_easting, utm_northing, context_num, find_num):
        """This function gets the batch information from the database

        Args:
            utm_easting (str): Easting of the find
            utm_northing (str): Northing of the find
            context_num (str): Context of the find
            find_num (str): Find number of the find

        Returns:
            tuple: (batch_year, batch_number, batch_piece)
        """
        if not self.conn:
            self.conn = psycopg2.connect(**READ_SETTINGS)
        conn = self.conn

        try:
            cursor = conn.cursor()
            query = """
            SELECT "3d_batch_year", "3d_batch_number", "3d_batch_piece" 
            FROM object.finds
            WHERE
            finds.area_utm_easting_meters=%s  AND
            finds.area_utm_northing_meters=%s AND
            finds.context_number=%s           AND
            finds.find_number=%s;
            """
            cursor.execute(query, (utm_easting, utm_northing, context_num, find_num))

            record = cursor.fetchall()
            if len(record) > 1:
                logging.error("Error, detected duplicate entry!")
                return None, None, None
            elif len(record) == 0:
                return None, None, None
            else:
                logging.info(
                    "the find of (%i, %i, %i, %i) has the record %s",
                    utm_easting,
                    utm_northing,
                    context_num,
                    find_num,
                    record,
                )
                return record[0]

        except psycopg2.Error as error:
            logging.error("Error while connecting to PostgreSQL: %s", error)
        finally:
            if conn:
                cursor.close()

    def update_match_info(
        self,
        utm_easting,
        utm_northing,
        context_num,
        find_num,
        new_batch_num,
        new_sherd_num,
        new_year,
    ):
        """This function updates the batch information of a certain find in the database

        Args:
            utm_easting (str): Easting of the find
            utm_northing (str): Northing of the find
            context_num (str): Context of the find
            find_num (str): Find number of the find
            new_batch_num (str): The batch number of the 3d model of the find
            new_sherd_num (str): The sherd number of the 3d model of the find
            new_year (str): The year number of the 3d model of the find
        """
        if not self.conn:
            self.conn = psycopg2.connect(**READ_SETTINGS)
        conn = self.conn
        try:
            conn = psycopg2.connect(**WRITE_SETTINGS)
            cursor = conn.cursor()

            query_select = """
            SELECT "3d_batch_number", "3d_batch_piece" , "3d_batch_year"
            FROM object.finds
            WHERE
            finds.area_utm_easting_meters=%s  AND
            finds.area_utm_northing_meters=%s AND
            finds.context_number=%s           AND
            finds.find_number=%s;
            """

            query_update = """
            UPDATE object.finds 
            SET "3d_batch_number" = %s, "3d_batch_piece" = %s, "3d_batch_year" = %s
            WHERE finds.area_utm_easting_meters = %s and finds.area_utm_northing_meters = %s and finds.context_number = %s and finds.find_number = %s;
            """

            cursor.execute(
                query_select, (utm_easting, utm_northing, context_num, find_num)
            )

            record = cursor.fetchall()
            if len(record) > 1:
                logging.error("Error, detected duplicate entry!")
            else:
                batch_number, sherd_number, year_number = record[0]
                if (
                    batch_number == new_batch_num
                    and sherd_number == new_sherd_num
                    and year_number == new_year
                ):
                    pass
                else:
                    logging.info("Updating...")
                    cursor.execute(
                        query_update,
                        (
                            new_batch_num,
                            new_sherd_num,
                            new_year,
                            utm_easting,
                            utm_northing,
                            context_num,
                            find_num,
                        ),
                    )

                    updated_rows = cursor.rowcount
                    if updated_rows <= 1:
                        conn.commit()
                        logging.info(
                            "Updated with (new_batch_num, new_sherd_num, new_year): (%i, %i, %i)",
                            new_batch_num,
                            new_sherd_num,
                            new_year,
                        )

        except psycopg2.Error as error:
            logging.error("Error while connecting to PostgreSQL: %s", error)
        finally:
            if conn:
                cursor.close()
