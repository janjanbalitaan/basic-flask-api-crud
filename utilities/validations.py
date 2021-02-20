from flask import request
from cerberus import Validator
from functools import wraps
from flask_jwt_extended import get_jwt_identity
import json
from uuid import uuid4, UUID
from utilities.constants import Constant


response = {
    'status': 'error',
    'message': 'error'
}
constants = Constant.get_instance()


def generic_uuid4_validator(str):
    try:
        val = UUID(str, version=4)
        return True
    except:
        return False


def uuid4_validator(field, value, error):
    if value is not None and value != "":
        if not generic_uuid4_validator(value):
            error(field, "Must be in a valid format of uuidv4")


def validate_user_create(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        schema = {
            'email': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            },
            'username': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'minlength': 3,
                'maxlength': 64
            },
            'password': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'minlength': 8,
                'maxlength': 64
                # add validation for password format
            }
        }

        data = request.get_json()
        if data is None or data == {}:
            response['message'] = 'JSON body is required'
            return response, 400

        v = Validator(schema)
        try:
            if not v.validate(data):
                response['message'] = f'error: {v.errors}'
                return response, 400
        except:
            response['message'] = f'error: {v.errors}'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_post_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        grant_type_schema = {
            'type': 'string',
            'empty': False,
            'nullable': False,
            'required': True,
            'allowed': constants.get_supported_grant_types()
        }
        schema = {
            "password": {
                'username': {
                    'type': 'string',
                    'empty': False,
                    'nullable': False,
                    'required': True,
                    'minlength': 3,
                    'maxlength': 64
                },
                'password': {
                    'type': 'string',
                    'empty': False,
                    'nullable': False,
                    'required': True,
                    'minlength': 8,
                    'maxlength': 64
                    # add validation for password format
                },
                'grant_type': grant_type_schema
            },
            "refresh_token": {
                'refresh_token': {
                    'type': 'string',
                    'empty': False,
                    'nullable': False,
                    'required': True,
                    'maxlength': 64, 
                    'validator': uuid4_validator
                },
                'grant_type': grant_type_schema
            }
        }

        data = request.get_json()
        if data is None or data == {}:
            response['message'] = 'JSON body is required'
            return response, 400


        if 'grant_type' not in data:
            response['message'] = 'grant_type is required'
            return response, 400


        if data['grant_type'] not in constants.get_supported_grant_types():
            response['message'] = 'grant_type is invalid'
            return response, 400

        
        v = Validator(schema.get(data['grant_type']))
        try:
            if not v.validate(data):
                response['message'] = f'error: {v.errors}'
                return response, 400
        except:
            response['message'] = f'error: {v.errors}'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_delete_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        refresh_token = request.args.get('refresh_token')
        if refresh_token is None or refresh_token == "" or not generic_uuid4_validator(refresh_token):
            response['message'] = 'refresh_token is required'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def is_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = json.loads(get_jwt_identity())
        if current_user["membership_type"] != 0:
            return {
                'status': 'error',
                'message': 'Not authorized to access this endpoint'
            }, 401
            
        return f(*args, **kwargs)

    
    return decorated


def validate_post_list(f):
    @wraps(f)
    def decorated(*args, **kwargs):
    
        schema = {
            'title': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 256
            },
            'user_id': {
                'type': 'string',
                'empty': False,
                'nullable': True,
                'required': False,
                'maxlength': 64, 
                'validator': uuid4_validator
            }
        }

        data = request.get_json()
        if data is None or data == {}:
            response['message'] = 'JSON body is required'
            return response, 400

        v = Validator(schema)
        try:
            if not v.validate(data):
                response['message'] = f'error: {v.errors}'
                return response, 400
        except:
            response['message'] = f'error: {v.errors}'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_put_list(f):
    @wraps(f)
    def decorated(*args, **kwargs):
    
        schema = {
            'id': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 64, 
                'validator': uuid4_validator
            },
            'title': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 256
            },
            'user_id': {
                'type': 'string',
                'empty': False,
                'nullable': True,
                'required': False,
                'maxlength': 64, 
                'validator': uuid4_validator
            }
        }

        data = request.get_json()
        if data is None or data == {}:
            response['message'] = 'JSON body is required'
            return response, 400

        v = Validator(schema)
        try:
            if not v.validate(data):
                response['message'] = f'error: {v.errors}'
                return response, 400
        except:
            response['message'] = f'error: {v.errors}'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_delete_list(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        id = request.args.get('id')
        if id is None or id == "" or not generic_uuid4_validator(id):
            response['message'] = 'id is required'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_get_card(f):
    @wraps(f)
    def decorated(*args, **kwargs):
    
        list_id = request.args.get('list_id')
        if list_id is None or list_id == "" or not generic_uuid4_validator(list_id):
            response['message'] = 'list id is required'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_post_card(f):
    @wraps(f)
    def decorated(*args, **kwargs):
    
        schema = {
            'list_id': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 64, 
                'validator': uuid4_validator
            },
            'title': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 256
            },
            'description': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 512
            }
        }

        data = request.get_json()
        if data is None or data == {}:
            response['message'] = 'JSON body is required'
            return response, 400

        v = Validator(schema)
        try:
            if not v.validate(data):
                response['message'] = f'error: {v.errors}'
                return response, 400
        except:
            response['message'] = f'error: {v.errors}'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_put_card(f):
    @wraps(f)
    def decorated(*args, **kwargs):
    
        schema = {
            'id': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 64, 
                'validator': uuid4_validator
            },
            'title': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 256
            },
            'description': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 512
            }
        }

        data = request.get_json()
        if data is None or data == {}:
            response['message'] = 'JSON body is required'
            return response, 400

        v = Validator(schema)
        try:
            if not v.validate(data):
                response['message'] = f'error: {v.errors}'
                return response, 400
        except:
            response['message'] = f'error: {v.errors}'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_delete_card(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        id = request.args.get('id')
        if id is None or id == "" or not generic_uuid4_validator(id):
            response['message'] = 'id is required'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_get_comment(f):
    @wraps(f)
    def decorated(*args, **kwargs):
    
        card_id = request.args.get('card_id')
        id = request.args.get('id')
        if card_id is None or card_id == "" or not generic_uuid4_validator(card_id):
            response['message'] = 'card id is required'
            return response, 400


        if id is not None and (id == "" or not generic_uuid4_validator(id)):
            response['message'] = 'id is required'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_post_comment(f):
    @wraps(f)
    def decorated(*args, **kwargs):
    
        schema = {
            'card_id': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 64, 
                'validator': uuid4_validator
            },
            'reply_to': {
                'type': 'string',
                'empty': False,
                'nullable': True,
                'required': True,
                'maxlength': 64, 
                'validator': uuid4_validator
            },
            'content': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 512
            }
        }

        data = request.get_json()
        if data is None or data == {}:
            response['message'] = 'JSON body is required'
            return response, 400

        v = Validator(schema)
        try:
            if not v.validate(data):
                response['message'] = f'error: {v.errors}'
                return response, 400
        except:
            response['message'] = f'error: {v.errors}'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_put_comment(f):
    @wraps(f)
    def decorated(*args, **kwargs):
    
        schema = {
            'id': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 64, 
                'validator': uuid4_validator
            },
            'content': {
                'type': 'string',
                'empty': False,
                'nullable': False,
                'required': True,
                'maxlength': 512
            }
        }

        data = request.get_json()
        if data is None or data == {}:
            response['message'] = 'JSON body is required'
            return response, 400

        v = Validator(schema)
        try:
            if not v.validate(data):
                response['message'] = f'error: {v.errors}'
                return response, 400
        except:
            response['message'] = f'error: {v.errors}'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated


def validate_delete_comment(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        id = request.args.get('id')
        if id is None or id == "" or not generic_uuid4_validator(id):
            response['message'] = 'id is required'
            return response, 400

            
        return f(*args, **kwargs)

    
    return decorated