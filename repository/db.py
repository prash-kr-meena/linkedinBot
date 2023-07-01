import os.path

from config.db_config import db_filename
from database import sqlitedb
from definitions import ROOT_DIR

db_path = os.path.join(ROOT_DIR, f"{db_filename}")
dbm = sqlitedb.SQLiteDB(f"file:{db_path}").open(txn_type=sqlitedb.TransactionType.DEFERRED)
# dbm = sqlitedb.SQLiteDB(f"file:{db_path}").open(txn_type=sqlitedb.TransactionType.IMMEDIATE)

# dbm = sqlitedb.SQLiteDB(f"file:{db_filename}").open(txn_type=sqlitedb.TransactionType.DEFERRED)

print("Creating DB Tables If not Present")
dbm.execute_script("""
CREATE TABLE IF NOT EXISTS main.company
(
    company_id   text PRIMARY KEY,
    company_name text NOT NULL,
    company_link text NOT NULL UNIQUE 
);

CREATE TABLE IF NOT EXISTS main.job
(
    job_link           text PRIMARY KEY,
    job_title          text NOT NULL,
    referral_submitted int DEFAULT 0,
    company_id         int  NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company (company_id)
);

CREATE TABLE IF NOT EXISTS main.connection
(
    connection_link   text PRIMARY KEY,
    connection_name   text NOT NULL,
    company_id        text NOT NULL,
    last_message_time text,
    FOREIGN KEY (company_id) REFERENCES company (company_id)
);
""")

if __name__ == '__main__':
    data = dbm.fetch_rowset(
        query="SELECT * FROM job"
    )
    print(data)

    dbm.prepare_and_execute(
        query="INSERT INTO job values ('job_link', 'job_title', 1, 'company_id')"
    )

    data = dbm.fetch_rowset(
        query="SELECT * FROM job"
    )
    print(data)

    dbm.prepare_and_execute(
        query="INSERT INTO job values (:job_link, :job_title, :referral_submitted, :company_id)",
        query_params={
            "job_link": "some link",
            "job_title": "some job_title",
            "referral_submitted": 1,
            "company_id": "some company_id"
        }
    )

    data = dbm.fetch_rowset(
        query="SELECT * FROM job"
    )
    print(data)

    fileName = dbm.fetch_rowset(
        query="SELECT file FROM pragma_database_list() WHERE name = 'main';"
    )
    print(fileName)
