
from flask_migrate import Migrate
from app.create_app import create_app
from app import  db
from flask_cors import CORS

app = create_app()
app.config["CORS_HEADERS"] = "Content-Type"
CORS(app, resources={r"/*": {"origins": "*"}})


migrate = Migrate(app, db, compare_type=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)