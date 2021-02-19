from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, fields, marshal_with, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from utilities.response import Response
from utilities.validations import validate_user_create
from models import db, User
import json


response = Response.get_instance()
generic_fields = response.get_generic_response_fields()
user_fields = {
    'id': fields.String,
    'created': fields.DateTime,
    'updated': fields.DateTime,
    'username': fields.String,
    'email': fields.String,
    'membership': fields.Integer(default=1)
}
user_list_fields = fields.List(fields.Nested(user_fields.copy()))
users_list = generic_fields.copy()
users_list['data'] = user_list_fields
user_resp = generic_fields.copy()
user_resp['data'] = user_fields


class Users(Resource):

    @jwt_required()
    @marshal_with(users_list)
    def get(self):
        current_user = json.loads(get_jwt_identity())
        if current_user["membership_type"] != 0:
            return {
                'status': 'error',
                'message': 'Not authorized to access this endpoint'
            }, 401


        limit = request.args.get('limit', 30)
        offset = request.args.get('offset', 0)
        users = User.query.limit(limit).offset(offset).all()
        users = [user.to_dict() for user in users]
        return {
            'status': 'ok',
            'message': 'Successfully fetched the users',
            'data': users
        }, 200


    @marshal_with(generic_fields)
    @validate_user_create
    def post(self):
        resp = {
            "status": "ok",
            "message": "Successfully created the users",
        }
        data = request.get_json()
        password = User.generate_password(data['password'])
        try:
            user = User(username=data['username'], password=password, email=data['email'])
            db.session.add(user)    
            db.session.commit()
            resp['data'] = user
        except IntegrityError:
            db.session.rollback()
            resp['status'] = 'error'
            resp['message'] = "Username or Email is already taken"
            return resp, 409
        
        print(resp)

        return marshal(resp, user_resp), 200

