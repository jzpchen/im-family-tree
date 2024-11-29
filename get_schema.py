from app import app, db

with app.app_context():
    with db.engine.connect() as conn:
        tables = conn.execute(db.text("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"))
        with open('schema.sql', 'w') as f:
            for table in tables:
                f.write(f"{table[0]};\n\n")
