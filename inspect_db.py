import sqlite3

conn = sqlite3.connect("product_intelligence.db")
cur = conn.cursor()

tables = cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

print("=== TABLES IN DB ===")
for (name,) in tables:
    count = cur.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info([{name}])").fetchall()]
    idxs = [i[1] for i in cur.execute(f"PRAGMA index_list([{name}])").fetchall()]
    print(f"\n{name}: {count:,} rows")
    print(f"  columns : {cols}")
    if idxs:
        print(f"  indexes : {idxs}")

print("\n=== FOREIGN KEYS ===")
for (name,) in tables:
    fks = cur.execute(f"PRAGMA foreign_key_list([{name}])").fetchall()
    if fks:
        print(f"  {name}: {[(f[2], f[3], f[4]) for f in fks]}")

conn.close()
