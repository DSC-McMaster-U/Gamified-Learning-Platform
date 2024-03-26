from app.src.app import create_app, db
from app.src.models import User, Course

# To run the app, type "flask --app run_app.py run" into the terminal
app = create_app()

@app.cli.command("clear-db")
def clear_db_command():
    if input("The database will be fully cleared. Are you sure? (y/n): ").lower() == "y":
        db.drop_all()
        db.create_all()
        print("Database cleared.")
    else:
        print("Canceled command.")

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Course': Course}

if __name__ == "__main__":
    app.run()
