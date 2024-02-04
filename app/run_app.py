from app.src.app import create_app

# To run the app, type "flask --app run_app.py run" into the terminal
if __name__ == "__main__":
    app = create_app()
    app.run()
