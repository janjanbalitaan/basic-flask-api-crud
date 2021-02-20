from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, fields, marshal_with, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from utilities.response import Response
from utilities.validations import validate_post_list, validate_put_list, validate_delete_list, is_admin
from models import db, List, User
import json


resp = {
    "status": "ok",
    "message": "Successfully created the list",
}
response = Response.get_instance()
generic_fields = response.get_generic_response_fields()
card_fields = {
    'id': fields.String,
    'created': fields.DateTime,
    'modified': fields.DateTime,
    'title': fields.String,
    'description': fields.String,
    'user_id': fields.String,
    'list_id': fields.String
}
list_fields = {
    'id': fields.String,
    'created': fields.DateTime,
    'modified': fields.DateTime,
    'title': fields.String,
    'user_id': fields.String,
    'cards': fields.List(fields.Nested(card_fields.copy()))
}
lists_list = generic_fields.copy()
lists_list['data'] = fields.List(fields.Nested(list_fields.copy()))
lists_post= generic_fields.copy()
lists_post['data'] = list_fields


class Lists(Resource):

    @jwt_required()
    @marshal_with(lists_list)
    def get(self):
        current_user = json.loads(get_jwt_identity())
        limit = request.args.get('limit', 30)
        offset = request.args.get('offset', 0)
        user_id = request.args.get('id')
        lists = List.query
        if current_user['membership_type'] == 0:
            # can fetch all list or current list
            if user_id is None:
                lists = lists.filter(List.user_id==current_user['id'])
            else:
                if user_id != 'all':
                    lists = lists.filter(List.user_id==user_id)
        else:
            lists = lists.filter(List.user_id==current_user['id'])


        lists = lists.limit(limit).offset(offset).all()
        lists_data = []
        for lst in lists:
            l = lst.to_dict()
            l['cards'] = [c.to_dict() for c in lst.cards]
            lists_data.append(l)


        return {
            'status': 'ok',
            'message': 'Successfully fetched the lists',
            'data': lists_data
        }, 200


    @validate_post_list
    @jwt_required()
    @is_admin
    @marshal_with(generic_fields)
    def post(self):
        current_user = json.loads(get_jwt_identity())
        r = resp.copy()
        data = request.get_json()
        user_id = None
        if 'user_id' in data and data['user_id'] is not None:
            user = User.query.filter(User.id==data['user_id']).first()
            if user is None:
                r['status'] = 'error'
                r['message'] = 'user id is not valid'
                return r, 400
            user_id = user.id


        lst = List(title=data['title'], user_id=user_id)
        db.session.add(lst)
        db.session.commit()
        return r, 200


    @validate_put_list
    @jwt_required()
    @is_admin
    @marshal_with(generic_fields)
    def put(self):
        current_user = json.loads(get_jwt_identity())
        data = request.get_json()
        r = resp.copy()
        lst = List.query.filter(List.id==data['id']).first()

        if lst is None:
            r['status'] = 'error'
            r['message'] = 'list is not available for update'
            return r, 403


        if 'user_id' in data:
            if data['user_id'] is None:
                #unassigned member
                lst.user_id = None
            else:
                user = User.query.filter(User.id==data['user_id']).first()
                if user is None:
                    r['status'] = 'error'
                    r['message'] = 'user id is not valid'
                    return r, 400
                lst.user_id = user.id
        

        lst.title = data['title']
        db.session.commit()
            
        r['message'] = 'Succesfully updated the list'
        return r, 200


    @validate_delete_list
    @jwt_required()
    @is_admin
    @marshal_with(generic_fields)
    def delete(self):
        r = resp.copy()
        current_user = json.loads(get_jwt_identity())
        id = request.args.get('id')
        curr_list = List.query.filter(List.id==id).first()


        if curr_list is None:
            r['status'] = 'error'
            r['message'] = 'list is not found on the database'
            return r, 403


        db.session.delete(curr_list)
        db.session.commit()
        r['message'] = 'successfully deleted a list'
        return r, 200

