from flask import request
from flask_restful import Resource, fields, marshal, marshal_with
from flask_jwt_extended import create_access_token
from models import User, Token
from utilities.response import Response
from utilities.validations import validate_post_auth, validate_delete_auth
from sqlalchemy.exc import IntegrityError
from models import db, User
import json
from datetime import datetime


resp = {
    "status": "ok",
    "message": "Successfully logged in",
}
response = Response.get_instance()
generic_fields = response.get_generic_response_fields()
data_fields = {
    'id': fields.String,
    'username': fields.String,
    'email': fields.String,
    'membership_type': fields.Integer
}

class Auth(Resource):


    @validate_post_auth
    def post(self):
        data = request.get_json()

        
        if data['grant_type'] == 'password':
            user = User.query.filter(User.username==data['username']).first()


            if user is None:
                resp['status'] = 'error'
                resp['message'] = 'user is not found on the database'
                return marshal(resp, generic_fields), 401


            if not User.is_match_password(user.password, data['password']):
                resp['status'] = 'error'
                resp['message'] = 'user and password doesnt match'
                return marshal(resp, generic_fields), 401

            user_id = user.id


        if data['grant_type'] == 'refresh_token':
            curr_token = Token.query.filter(Token.id==data['refresh_token'], Token.expiration>datetime.now()).first()


            if curr_token is None:
                resp['status'] = 'error'
                resp['message'] = 'refresh token is not found on the database'
                return marshal(resp, generic_fields), 401

            user_id = curr_token.user_id
            user = User.query.filter(User.id==user_id).first()


            if user is None:
                resp['status'] = 'error'
                resp['message'] = 'user is not found on the database'
                return marshal(resp, generic_fields), 401


        jwt_data = json.dumps(marshal(user, data_fields))
        access_token = create_access_token(identity=jwt_data)
        token = Token(user_id=user_id)
        db.session.add(token)
        db.session.commit()


        resp['data'] = {
            'access_token': access_token,
            'refresh_token': str(token.id)
        }
        return resp, 200

    
    @marshal_with(generic_fields)
    @validate_delete_auth
    def delete(self):
        refresh_token = request.args.get('refresh_token')
        curr_token = Token.query.filter(Token.id==refresh_token, Token.expiration>datetime.now()).first()


        if curr_token is None:
            resp['status'] = 'error'
            resp['message'] = 'refresh token is not found on the database'
            return resp, 401

        db.session.delete(curr_token)
        db.session.commit()
        resp['message'] = 'successfully revoked a token'
        return resp, 401


