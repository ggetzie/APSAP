import psycopg2


def list_all_tabels():
    try:
        conn = psycopg2.connect(
            database="archaeology",
            host="localhost",
            user="dbro",
            password="dbro",
            port="5432",
            sslmode="disable",
        )

        cursor = conn.cursor()

        query = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
        cursor.execute(query)
        # Fetch result
        record = cursor.fetchall()
        print(record, "\n")

    except (Exception) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")


def get_pottery_sherd_info(utm_easting, utm_northing, context_num, find_num):
    try:
        conn = psycopg2.connect(
            database="archaeology",
            host="localhost",
            user="dbro",
            password="dbro",
            port="5432",
            sslmode="disable",
        )

        cursor = conn.cursor()

        query = 'SELECT "3d_batch_number", "3d_batch_piece" FROM object.finds WHERE finds.area_utm_easting_meters = {} and finds.area_utm_northing_meters = {} and finds.context_number = {} and finds.find_number = {};'.format(
            utm_easting, utm_northing, context_num, find_num
        )
        cursor.execute(query)
        # Fetch result
        record = cursor.fetchall()
        if len(record) > 1:
            print("Error, detected duplicate entry!")
            return None
        else:
            # print(record, "\n")
            return record[0]

    except (Exception) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cursor.close()
            conn.close()


def update_match_info(
    utm_easting, utm_northing, context_num, find_num, new_batch_num, new_sherd_num
):
    try:
        conn = psycopg2.connect(
            database="archaeology",
            host="localhost",
            user="dbrw",
            password="dbrw",
            port="5432",
            sslmode="disable",
        )

        cursor = conn.cursor()

        query_select = 'SELECT "3d_batch_number", "3d_batch_piece" FROM object.finds WHERE finds.area_utm_easting_meters = {} and finds.area_utm_northing_meters = {} and finds.context_number = {} and finds.find_number = {};'.format(
            utm_easting, utm_northing, context_num, find_num
        )
        query_update = 'UPDATE object.finds SET "3d_batch_number" = {}, "3d_batch_piece" = {} WHERE finds.area_utm_easting_meters = {} and finds.area_utm_northing_meters = {} and finds.context_number = {} and finds.find_number = {};'.format(
            new_batch_num,
            new_sherd_num,
            utm_easting,
            utm_northing,
            context_num,
            find_num,
        )

        cursor.execute(query_select)
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
                cursor.execute(query_update)
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


# list_all_tabels()
# get_pottery_sherd_info(478130,4419430,43,1)
# update_match_info(478130, 4419430, 43, 1, 0, 0)
# get_pottery_sherd_info(478130,4419430,43,1)
