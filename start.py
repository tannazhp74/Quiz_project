import sys

sys.path.append('./app')
from create_app import create_app
from flask_migrate import Migrate

app = create_app()

from app import db

migrate = Migrate(app, db)


@app.after_request
def after_request(response):
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Credentials', 'true')
    response.headers.set('Access-Control-Allow-Headers', '*')
    response.headers.set('Access-Control-allow-Methods', '*')
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
