from app import app, db

def init_db():
    with app.app_context():
        # Create tables
        with open('schema.sql', 'r') as f:
            schema = f.read()
            for statement in schema.split(';'):
                if statement.strip():
                    db.session.execute(db.text(statement))
        db.session.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
