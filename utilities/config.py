import datetime
from utilities.constants import Constant


constants = Constant.get_instance()


class Configuration(object):
    SQLALCHEMY_DATABASE_URI = constants.get_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    JWT_SECRET_KEY = constants.get_jwt_secret()
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)