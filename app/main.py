import os
from dotenv import load_dotenv
import mysql.connector
import scraper


def criar_tabela():
    cnx = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
    cursor = cnx.cursor()

    with open("init/ini.sql", "r") as f:
        ddl = f.read()

    cursor.execute(ddl)
    cnx.commit()

    cursor.close()
    cnx.close()


def main():
    criar_tabela()
    scraper.main()

if __name__ == "__main__":
    main()
