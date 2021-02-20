from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, User
import sys
from utilities.config import Configuration
from utilities.constants import Constant


constants = Constant.get_instance()


def create_app(config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config)


    from app import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')


    db.init_app(app)
    jwt = JWTManager(app)


    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return {
            'status': 'error',
            'message': 'The request authorization has invalid bearer token'
        }, 401


    @jwt.expired_token_loader
    def expired_token_callback(self, callback):
        return {
            'status': 'error',
            'message': 'The bearer token has already expired. Please try to login again.'
        }, 401


    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return {
            'status': 'error',
            'message': 'The request authorization has invalid bearer token'
        }, 401


    @jwt.needs_fresh_token_loader
    def fresh_token_callback(self, callback):
        return {
            'status': 'error',
            'message': 'The request authorization has invalid bearer token'
        }, 401


    return app


if __name__ == "__main__":
    if len(sys.argv) > 1 and '--testing' in sys.argv:
        print('You are running the application in test mode')
        is_debug = True
    else:
        print('You are running the application in production mode')
        is_debug = False


    app = create_app(Configuration)
    with app.app_context():
        # create admin account here
        try:
            db.session.add(User(**constants.get_admin_credentials(), membership_type=0))
            db.session.commit()
            print('Successfully saved admin credentials')
        except:
            #will error if it already exists
            print('Skipped admin credentials creation')
            pass
    app.run(debug=is_debug)