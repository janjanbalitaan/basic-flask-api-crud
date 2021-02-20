from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, fields, marshal_with, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, desc
from utilities.response import Response
from utilities.validations import validate_get_card, validate_post_card, validate_put_card, validate_delete_card
from models import db, Card, List, Comment
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
    'card_id': fields.String,
    'user_id': fields.String,
}
card_fields = {
    'id': fields.String,
    'created': fields.DateTime,
    'modified': fields.DateTime,
    'title': fields.String,
    'description': fields.String,
    'user_id': fields.String,
    'list_id': fields.String,
    'comments': fields.List(fields.Nested(comment_fields.copy()))
}
cards_list = generic_fields.copy()
cards_list['data'] = fields.List(fields.Nested(card_fields.copy()))


class Cards(Resource):


    @validate_get_card
    @jwt_required()
    @marshal_with(cards_list)
    def get(self):
        current_user = json.loads(get_jwt_identity())
        limit = request.args.get('limit', 30)
        offset = request.args.get('offset', 0)
        list_id = request.args.get('list_id')
        lst = List.query.filter(List.id==list_id)

        if current_user['membership_type'] != 0:
            lst = lst.filter(List.user_id==current_user['id'])

        lst = lst.first()
        if lst is None:
            r['status'] = 'error'
            r['message'] = 'list is not available for update'
            return r, 403

        comment_counts = db.session.query(Comment.card_id, func.count(Comment.id).label('count')).group_by(Comment.card_id).subquery()
        cards = Card.query.join(comment_counts, comment_counts.c.card_id==Card.id, isouter=True)\
            .filter(Card.list_id==lst.id).order_by(desc(func.count(comment_counts.c.count)))\
            .group_by(Card.id).limit(limit).offset(offset).all()
        cards_data = []
        for card in cards:
            c = card.to_dict()
            c['comments'] = [comment.to_dict() for comment in card.comments.filter(Comment.reply_to==None).order_by(Comment.created).limit(3).all()]
            cards_data.append(c)

            
        return {
            'status': 'ok',
            'message': 'Successfully fetched the cards',
            'data': cards_data
        }, 200


    @validate_post_card
    @jwt_required()
    @marshal_with(generic_fields)
    def post(self):
        current_user = json.loads(get_jwt_identity())
        data = request.get_json()
        r = resp.copy()
        lst = List.query.filter(List.id==data['list_id'])


        if current_user['membership_type'] != 0:
            lst = lst.filter(List.user_id==current_user['id'])


        lst = lst.first()
        if lst is None:
            r['status'] = 'error'
            r['message'] = 'list is not available for card creation'
            return r, 403


        card = Card(list_id=lst.id, title=data['title'], description=data['description'], user_id=current_user['id'])
        db.session.add(card)
        db.session.commit()
        r['message'] = 'Succesfully created the card'
        return r, 200


    @validate_put_card
    @jwt_required()
    @marshal_with(generic_fields)
    def put(self):
        current_user = json.loads(get_jwt_identity())
        data = request.get_json()
        r = resp.copy()
        card = Card.query.filter(Card.id==data['id'])

        if current_user['membership_type'] != 0:
            card = card.filter(Card.user_id==current_user['id'])


        card = card.first()
        if card is None:
            r['status'] = 'error'
            r['message'] = 'card is not available for update'
            return r, 403

        
        card.title = data['title']
        card.description = data['description']
        db.session.commit()
        r['message'] = 'Succesfully updated the card'
        return r, 200


    @validate_delete_card
    @jwt_required()
    @marshal_with(generic_fields)
    def delete(self):
        r = resp.copy()
        current_user = json.loads(get_jwt_identity())
        id = request.args.get('id')
        card = Card.query.filter(Card.id==id)

        if current_user['membership_type'] != 0:
            card = card.filter(Card.user_id==current_user['id'])


        card = card.first()
        if card is None:
            r['status'] = 'error'
            r['message'] = 'card is not found on the database'
            return r, 403


        db.session.delete(card)
        db.session.commit()
        r['message'] = 'successfully deleted a card'
        return r, 200

