import sqlite3
conn = sqlite3.connect("product_intelligence.db")
cur = conn.cursor()
tables = cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()
print("=== CURRENT DB STATE ===")
total_rows = 0
for (name,) in tables:
    if name.startswith("_tmp_"):
        continue
    count = cur.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
    idxs = [i[1] for i in cur.execute(f"PRAGMA index_list([{name}])").fetchall()]
    total_rows += count
    print(f"  {name:<50} {count:>10,} rows  indexes={len(idxs)}")
print(f"\n  TOTAL ROWS ACROSS ALL TABLES: {total_rows:,}")

print("\n=== FOREIGN KEY CHECK ===")
fk_checks = [
    ("orders missing customer",       "SELECT COUNT(*) FROM orders o LEFT JOIN customers c ON o.customer_id=c.customer_id WHERE c.customer_id IS NULL"),
    ("order_items missing order",     "SELECT COUNT(*) FROM order_items oi LEFT JOIN orders o ON oi.order_id=o.order_id WHERE o.order_id IS NULL"),
    ("order_items missing product",   "SELECT COUNT(*) FROM order_items oi LEFT JOIN products p ON oi.product_id=p.product_id WHERE p.product_id IS NULL"),
    ("order_items missing seller",    "SELECT COUNT(*) FROM order_items oi LEFT JOIN sellers s ON oi.seller_id=s.seller_id WHERE s.seller_id IS NULL"),
    ("order_payments missing order",  "SELECT COUNT(*) FROM order_payments op LEFT JOIN orders o ON op.order_id=o.order_id WHERE o.order_id IS NULL"),
    ("reviews missing order",         "SELECT COUNT(*) FROM reviews r LEFT JOIN orders o ON r.order_id=o.order_id WHERE o.order_id IS NULL"),
]
for label, q in fk_checks:
    n = cur.execute(q).fetchone()[0]
    status = "OK" if n == 0 else f"VIOLATION ({n:,})"
    print(f"  {label:<40} {status}")

conn.close()
