"""Usage examples for sqlitedb.SQLiteDB"""
import pprint

from database import sqlitedb as sdb  # Normal usage

pp = pprint.PrettyPrinter(indent=4)

create_words_table = "CREATE TABLE IF NOT EXISTS words(id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT);"
insert_words = {
    "query": "INSERT INTO words VALUES (?, ?);",
    "params": [
        (None, 'Python'), (None, 'is'), (None, 'a'), (None, 'very'),
        (None, 'cool'), (None, 'programming'), (None, 'language'),
        (None, 'sexy'), (None, 'problem '), (None, 'sqlite')
    ]
}

insert_words_by_param_name = {
    "query": "INSERT INTO words VALUES (:id, :word);",
    "params": {
        "id": None,
        "word": "palak"
    }
}
select_words = {
    "query": "SELECT * FROM words WHERE id > :id;",
    "params": {"id": 6},
}

function_list_sql = "SELECT * FROM pragma_function_list() ORDER BY name, narg;"
function_list_sql_qmark = {
    "query": "SELECT * FROM pragma_function_list() WHERE name like ? and narg > ?;",
    "params": ("s%", 1),
}
function_list_sql_named = {
    "query": "SELECT * FROM pragma_function_list() WHERE name like :name and narg > :narg;",
    "params": {"name": "s%", "narg": 1},
}

# txn_type=sdb.TransactionType.DEFERRED - default, matching the default behavior
# of the sqlite3 module, with implicit transactions started before UPD/DEL/INS
# dbm = sdb.SQLiteDB(":memory:").open(txn_type=sdb.TransactionType.DEFERRED)
dbm = sdb.SQLiteDB("file:linkedin_referral.db").open(txn_type=sdb.TransactionType.DEFERRED)

dbm.execute_nonquery(create_words_table)
res = dbm.execute_nonquery(insert_words_by_param_name["query"], insert_words_by_param_name["params"])

res = dbm.execute_nonquery(insert_words["query"], insert_words["params"])
dbm.commit()
query = select_words["query"]
params = select_words["params"]
word_list = dbm.fetch_rowset(query, params)
pp.pprint(word_list)

dbm.execute_nonquery("""
CREATE TABLE IF NOT EXISTS company_new
(
    company_id   text PRIMARY KEY,
    company_name text NOT NULL,
    company_link text NOT NULL UNIQUE 
);
""")

dbm.execute_nonquery("""
CREATE TABLE IF NOT EXISTS job_new
(
    job_link           text PRIMARY KEY,
    job_title          text NOT NULL,
    referral_submitted int DEFAULT 0,
    company_id         int  NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company (company_id)
);
""")

dbm.execute_nonquery("""
CREATE TABLE IF NOT EXISTS connection_new
(
    connection_link   text PRIMARY KEY,
    connection_name   text NOT NULL,
    company_id        text NOT NULL,
    last_message_time text,
    FOREIGN KEY (company_id) REFERENCES company (company_id)
);
""")

data = dbm.fetch_rowset(
    query="SELECT * FROM job_new"
)
print(data)

dbm.prepare_and_execute(
    query="INSERT INTO company_new values ('company_id', 'company_name','company_link')"
)
dbm.prepare_and_execute(
    query="INSERT INTO job_new values ('job_link', 'job_title', 1, 'company_id')"
)

data = dbm.fetch_rowset(
    query="SELECT * FROM job_new"
)
print(data)

dbm.prepare_and_execute(
    query="INSERT INTO job_new values (:job_link, :job_title, :referral_submitted, :company_id)",
    query_params={
        "job_link": "some link",
        "job_title": "some job_title",
        "referral_submitted": 1,
        "company_id": "company_id"
    }
)

data = dbm.fetch_rowset(
    query="SELECT * FROM job_new"
)
print(data)

fileName = dbm.fetch_rowset(
    query="SELECT file FROM pragma_database_list() WHERE name = 'main';"
)
print(fileName)
dbm.commit()

#
# # ========================
# # ===== Fetch Rowset =====
# # ========================
#
# query = function_list_sql
# function_list = dbm.fetch_rowset(query)  # ->fetchall
# pp.pprint(function_list)
#
# query = function_list_sql
# function_list = dbm.fetch_json_rowset(query)  # Fetch all rows via json package and fetchone
# pp.pprint(function_list)
#
# # ========================
# # ===== Get Columns ======
# # ========================
#
# query = function_list_sql
# dbm.prepare_and_execute(query)
# column_names = dbm.column_names()
# print(column_names)
#
# # ===============================
# # ===== Parameterized Query =====
# # ===============================
#
# query = function_list_sql_qmark["query"]
# params = function_list_sql_qmark["params"]
# function_list = dbm.fetch_rowset(query, params)  # ->fetchall
# pp.pprint(function_list)
#
# query = function_list_sql_named["query"]
# params = function_list_sql_named["params"]
# function_list = dbm.fetch_rowset(query, params)  # ->fetchall
# pp.pprint(function_list)
#
#
# # =======================
# # ===== Paged Query =====
# # =======================
#
# dbm.execute_nonquery(create_words_table)
# res = dbm.execute_nonquery(insert_words["query"], insert_words["params"])
# dbm.begin()
# dbm.commit()
# query = select_words["query"]
# params = select_words["params"]
# page = dbm.fetch_page(query, {"id": 12}, page_size=3)
# i = 0
# pages = []
# while len(page) > 0:
#     print(f"page {i}:")
#     pp.pprint(page)
#     pages.extend(page)
#     page = dbm.fetch_page()
#     i += 1
# pp.pprint(pages)
#
# page_gen = dbm.fetch_page_gen(query, {"id": 12}, page_size=3)
# i = 0
# pages = []
# page = next(page_gen)
# while len(page) > 0:
#     print(f"page {i}:")
#     pp.pprint(page)
#     pages.extend(page)
#     page = next(page_gen)
#     i += 1
