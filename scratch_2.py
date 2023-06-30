"""Usage examples for sqlitedb.SQLiteDB"""

import pprint

try:
    import database.sqlitedb as sdb  # This file sits next to sqlitedb.py
except:
    from database import sqlitedb as sdb  # Normal usage

pp = pprint.PrettyPrinter(indent=4)

create_words_table = "CREATE TABLE IF NOT EXISTS words(id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT);"
select_words = {
    "query": "SELECT * FROM words WHERE id < :id;",
    "params": {"id": 6},
}
insert_words = {
    "query": "INSERT INTO words VALUES (?, ?);",
    "params": [
        (None, 'Python'), (None, 'is'), (None, 'a'), (None, 'very'),
        (None, 'cool'), (None, 'programming'), (None, 'language')
    ]
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
dbm = sdb.SQLiteDB("file:database").open(txn_type=sdb.TransactionType.DEFERRED)

# ========================
# ===== Fetch Scalar =====
# ========================

query = "SELECT sqlite_version();"
version = dbm.fetch_scalar(query)  # fetched a string
print(version)

query = "SELECT CAST(replace(sqlite_version(), '.', '') AS INTEGER);"
version = dbm.fetch_scalar(query)  # fetched an integer
print(version)

# ========================
# ===== Fetch Rowset =====
# ========================

query = function_list_sql
function_list = dbm.fetch_rowset(query)  # ->fetchall
pp.pprint(function_list)

query = function_list_sql
function_list = dbm.fetch_json_rowset(query)  # Fetch all rows via json package and fetchone
pp.pprint(function_list)

# ========================
# ===== Get Columns ======
# ========================

query = function_list_sql
dbm.prepare_and_execute(query)
column_names = dbm.column_names()
print(column_names)

# ===============================
# ===== Parameterized Query =====
# ===============================

query = function_list_sql_qmark["query"]
params = function_list_sql_qmark["params"]
function_list = dbm.fetch_rowset(query, params)  # ->fetchall
pp.pprint(function_list)

query = function_list_sql_named["query"]
params = function_list_sql_named["params"]
function_list = dbm.fetch_rowset(query, params)  # ->fetchall
pp.pprint(function_list)

dbm.execute_nonquery(create_words_table)
res = dbm.execute_nonquery(insert_words["query"], insert_words["params"])
dbm.commit()
query = select_words["query"]
params = select_words["params"]
word_list = dbm.fetch_rowset(query, params)
pp.pprint(word_list)

# =======================
# ===== Paged Query =====
# =======================

dbm.execute_nonquery(create_words_table)
res = dbm.execute_nonquery(insert_words["query"], insert_words["params"])
dbm.begin()
dbm.commit()
query = select_words["query"]
params = select_words["params"]
page = dbm.fetch_page(query, {"id": 12}, page_size=3)
i = 0
pages = []
while len(page) > 0:
    print(f"page {i}:")
    pp.pprint(page)
    pages.extend(page)
    page = dbm.fetch_page()
    i += 1
pp.pprint(pages)

page_gen = dbm.fetch_page_gen(query, {"id": 12}, page_size=3)
i = 0
pages = []
page = next(page_gen)
while len(page) > 0:
    print(f"page {i}:")
    pp.pprint(page)
    pages.extend(page)
    page = next(page_gen)
    i += 1
