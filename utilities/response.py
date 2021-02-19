from flask_restful import fields


class Response:
    __instance = None

    
    @staticmethod
    def get_instance():
        if Response.__instance == None:
            Response()

        return Response.__instance


    def __init__(self):
        if Response.__instance != None:
            raise Exception("Already initialized")
        else:
            Response.__instance = self

    
    def get_generic_response_fields(self):
        return {
            'status': fields.String,
            'message': fields.String,
        }
