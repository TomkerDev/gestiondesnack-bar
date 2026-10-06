import sqlite3, pathlib
base = pathlib.Path("db/migrations")
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys=ON")
for f in sorted(base.glob("*.sql")):
    db.executescript(open(f, encoding="utf-8").read())
    print("OK", f.name)
tables = sorted(r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
trg = sorted(r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='trigger'"))
print("TABLES:", tables)
print("TRIGGERS:", trg)
