from dotenv import load_dotenv
import datetime
import os


load_dotenv()


class Constant:
    __instance = None

    
    @staticmethod
    def get_instance():
        if Constant.__instance == None:
            Constant()

        return Constant.__instance


    def __init__(self):
        if Constant.__instance != None:
            raise Exception("Already initialized")
        else:
            Constant.__instance = self

    
    def get_db_url(self, is_test=False):
        if is_test == True:
            return os.getenv('SQL_URI')


        return os.getenv('TEST_SQL_URI')


    def get_jwt_secret(self):
        return os.getenv('JWT_SECRET_KEY')

    
    def get_admin_credentials(self):
        return {
            'username': os.getenv('ADMIN_USERNAME'),
            'password': os.getenv('ADMIN_PASSWORD'),
            'email': os.getenv('ADMIN_EMAIL')
        }

    
    def get_supported_grant_types(self):
        return ['password', 'refresh_token']
