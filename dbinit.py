import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
   '''CREATE TABLE IF NOT EXISTS conditions (
        time        TIMESTAMPTZ       NOT NULL,
        location    TEXT              NOT NULL,
        temperature DOUBLE PRECISION  NULL,
        humidity    DOUBLE PRECISION  NULL
      );
      
      CREATE TABLE IF NOT EXISTS noise_sensor (
        time        TIMESTAMP         NOT NULL,
        sound       DOUBLE PRECISION  NULL
      );''']


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        
        cursor.close()


if __name__ == "__main__":
    
    url = os.getenv("DATABASE_URL")
    #url = "postgres://postgres:1423@localhost:5432/postgres"
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
