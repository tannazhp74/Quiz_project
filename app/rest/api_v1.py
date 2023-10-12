from flask import Blueprint
from flask_restx import Api
from rest.v1.rest import quiz_namespace

api_v1 = Blueprint('api_v1', __name__, url_prefix='/v1')
api = Api(api_v1, doc='/doc', version='1.0', title='Quiz')

api.add_namespace(quiz_namespace)


