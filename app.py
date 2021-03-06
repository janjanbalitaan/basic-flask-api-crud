from flask import Blueprint
from flask_restful import Api
from resources.users import Users
from resources.auth import Auth
from resources.lists import Lists
from resources.cards import Cards
from resources.comments import Comments


# initializations
api_bp = Blueprint('api', __name__)
api = Api(api_bp)


# routes
api.add_resource(Users, '/users')
api.add_resource(Auth, '/auth/token')
api.add_resource(Lists, '/lists')
api.add_resource(Cards, '/cards')
api.add_resource(Comments, '/comments')
