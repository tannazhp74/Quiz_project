
from flask_migrate import Migrate
from app.create_app import create_app
from app import  db

app = create_app()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db, compare_type=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

