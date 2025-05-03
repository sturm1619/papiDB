import logging
from string import Template
import csv
import sqlite3
from sqlite3 import DatabaseError

debug_messages: bool = True
error_template: str = Template("There was an error ${condition}.")
logger = logging.getLogger("initDB")
logging.basicConfig(filename="app.log", level=logging.INFO)

class PopulationError(BaseException): ...

def print_and_log(message: str) -> None:
    logger.info(message)
    print(message)

def handle_error(error: Exception, condition: str) -> None:
    message: str = error_template.substitute(condition=condition)
    if "logger" in globals(): logger.error(message)
    if debug_messages: error.add_note(message)
    print("Terminating process...")
    raise error

def default_null(data: str) -> str: return data if data else "NULL"

def main():
    """Script."""
    if debug_messages: print_and_log("Conneting to papiDB...")
    try:
        connection = sqlite3.connect(
            'papi.db', timeout=5.0, 
        )
        cursor = connection.cursor()
    except DatabaseError as error:
        handle_error(error, "connecting to the database")
    else:
        if debug_messages:
            print_and_log("Instantiating PapiDB. Creating Person table...")

    # Create Person table
    try:
        cursor.execute("DROP TABLE IF EXISTS Person;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Person(
                uid smallint primary key,
                alias text,
                name text,
                dob text,
                place text,
                note text
            );
        """)
    except DatabaseError as error: handle_error(error, "creating Person Table")
    else:
        if debug_messages: print_and_log("Person Table created. Populating table...")

    # Populate Person Table
    try:
        with open("T Cantante.txt", 'r', encoding="windows-1252") \
            as person_source:
            data = csv.reader(person_source)
            for row in data: cursor.execute(f"""
                    INSERT INTO Person (uid, alias, name)
                    values ({row[-1]}, '{row[0]}', '{default_null(row[1])}');
                """)

            connection.commit()
            cursor.execute("select * from Person;")
            if not cursor.fetchall():
                raise PopulationError
    except DatabaseError as error: handle_error(error, "populating Person Table")
    except PopulationError as error: handle_error(error, "populating Person Table")
    else:
        if debug_messages: print_and_log("Table populated. Creating Song Table.")

    # try:
    #     cursor.execute("DROP TABLE IF EXISTS Song;")
    #     cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS Song(
    #             uid tinyint primary key;
    #             title text
    #         );
    #     """)
    #     with open() as songs_file:
    #         ...


    # TODO: Model Person-Song relation/Create Person-Song table

    # Close connection
    connection.close()
if __name__ == "__main__": main()
