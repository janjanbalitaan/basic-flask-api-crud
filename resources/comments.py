from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, fields, marshal_with, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from utilities.response import Response
from utilities.validations import validate_get_comment, validate_post_comment, validate_put_comment, validate_delete_comment
from models import db, Comment, Card
import json


resp = {
    "status": "ok",
    "message": "Successfully created the list",
}
response = Response.get_instance()
generic_fields = response.get_generic_response_fields()
comment_fields = {
    'id': fields.String,
    'created': fields.DateTime,
    'modified': fields.DateTime,
    'content': fields.String,
    'user_id': fields.String,
    'card_id': fields.String,
    'reply_to': fields.String
}
comments_list = generic_fields.copy()
comments_list['data'] = fields.List(fields.Nested(comment_fields.copy()))


class Comments(Resource):


    @validate_get_comment
    @jwt_required()
    @marshal_with(comments_list)
    def get(self):
        current_user = json.loads(get_jwt_identity())
        r = resp.copy()
        limit = request.args.get('limit', 30)
        offset = request.args.get('offset', 0)
        card_id = request.args.get('card_id')
        #if not none, fetch the replies for the comment
        id = request.args.get('id')
        card = Card.query.filter(Card.id==card_id).first()

        if card is None:
            r['status'] = 'error'
            r['message'] = 'card is not found on the database'
            return r, 403

        # if not admin allow only fetching of owned cards
        if current_user['membership_type'] != 0 and current_user['id'] != card.user_id.__str__():
            r['status'] = 'error'
            r['message'] = 'card is not available for fetching of comments'
            return r, 403


        comments = Comment.query.filter(Comment.card_id==card_id, Comment.reply_to==id).limit(limit).offset(offset).all()
        comments = [comment.to_dict() for comment in comments]
        return {
            'status': 'ok',
            'message': 'Successfully fetched the cards',
            'data': comments
        }, 200


    @validate_post_comment
    @jwt_required()
    @marshal_with(generic_fields)
    def post(self):
        current_user = json.loads(get_jwt_identity())
        data = request.get_json()
        r = resp.copy()
        card = Card.query.filter(Card.id==data['card_id'])


        if current_user['membership_type'] != 0:
            card = card.filter(Card.user_id==current_user['id'])

        
        card = card.first()
        if card is None:
            r['status'] = 'error'
            r['message'] = 'card is not available for comment action'
            return r, 403


        if data['reply_to'] is not None:
            comment = Comment.query.filter(data['reply_to']==Comment.id, Comment.card_id==data['card_id']).first()
            if comment is None:
                r['status'] = 'error'
                r['message'] = 'comment id is not found for reply action'
                return r, 403


        comment = Comment(card_id=card.id, reply_to=data['reply_to'], content=data['content'], user_id=current_user['id'])
        db.session.add(comment)
        db.session.commit()
        r['message'] = 'Succesfully created a comment'
        return r, 200


    @validate_put_comment
    @jwt_required()
    @marshal_with(generic_fields)
    def put(self):
        current_user = json.loads(get_jwt_identity())
        data = request.get_json()
        r = resp.copy()
        comment = Comment.query.filter(Comment.id==data['id'])

        if current_user['membership_type'] != 0:
            comment = comment.filter(Comment.user_id==current_user['id'])


        comment = comment.first()
        if comment is None:
            r['status'] = 'error'
            r['message'] = 'comment is not available for update'
            return r, 403

        
        comment.content = data['content']
        db.session.commit()
        r['message'] = 'Succesfully updated the comment'
        return r, 200


    @validate_delete_comment
    @jwt_required()
    @marshal_with(generic_fields)
    def delete(self):
        r = resp.copy()
        current_user = json.loads(get_jwt_identity())
        id = request.args.get('id')
        comment = Comment.query.filter(Comment.id==id)

        if current_user['membership_type'] != 0:
            comment = comment.filter(Comment.user_id==current_user['id'])


        comment = comment.first()
        if comment is None:
            r['status'] = 'error'
            r['message'] = 'comment is not found on the database'
            return r, 403


        db.session.delete(comment)
        db.session.commit()
        r['message'] = 'successfully deleted a comment'
        return r, 200

