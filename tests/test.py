import unittest
from run import create_app
from utilities.config import TestConfiguration 
from utilities.constants import Constant
from models import db, User
from drop import drop
import json


app = create_app(TestConfiguration)
constants = Constant.get_instance()
content_type = 'application/json'
admin_refresh_token = None
normal_refresh_token = None
admin_access_token = None
normal_access_token = None


class TestCase(unittest.TestCase):

    def setUp(self):
        with app.app_context():
            db.create_all()
            self.app = app.test_client()

            # create admin account here
            try:
                db.session.add(User(**constants.get_admin_credentials(), membership_type=0))
                db.session.commit()
                print('Successfully saved admin credentials')
            except:
                #will error if it already exists
                print('Skipped admin credentials creation')
                pass

    
    def tearDown(self):
        drop(constants.get_db_url(is_test=True))


    def test_credentials(self):
        print('Testing Credentials')
        # with excess email
        admin_credentials = constants.get_admin_credentials_for_test()
        response = self.app.post('/api/auth/token', data=json.dumps(admin_credentials), content_type=content_type)
        self.assertEqual(response.status_code, 400)

        # remove email and add grant_type
        del admin_credentials['email']
        admin_credentials['grant_type'] = 'password'
        response = self.app.post('/api/auth/token', data=json.dumps(admin_credentials), content_type=content_type)
        admin_access_token = response.get_json()['data']['access_token']
        admin_refresh_token = response.get_json()['data']['refresh_token']
        self.assertEqual(response.status_code, 200)


        # login non-admin
        credentials = {
            'username': 'juan',
            'password': 'P@ssw0rd',
            'email': 'juan@juan.com'
        }
        normal_wrong_credentials = {
            'username': 'juan',
            'password': 'P@ssw0rd1',
            'grant_type': 'password'
        }
        normal_credentials = {
            'username': 'juan',
            'password': 'P@ssw0rd',
            'grant_type': 'password'
        }
        #register
        response = self.app.post('/api/users', data=json.dumps(credentials), content_type=content_type)
        self.assertEqual(response.status_code, 200)
        # duplicate issue
        response = self.app.post('/api/users', data=json.dumps(credentials), content_type=content_type)
        self.assertEqual(response.status_code, 409)

        # test login
        response = self.app.post('/api/auth/token', data=json.dumps(normal_wrong_credentials), content_type=content_type)
        self.assertEqual(response.status_code, 401)
        response = self.app.post('/api/auth/token', data=json.dumps(normal_credentials), content_type=content_type)
        normal_access_token = response.get_json()['data']['access_token']
        normal_refresh_token = response.get_json()['data']['refresh_token']
        self.assertEqual(response.status_code, 200)


        #refresh tokens
        normal_credentials = {
            'refresh_token': normal_refresh_token,
            'grant_type': 'refresh_token'
        }
        normal_wrong_credentials = {
            'refresh_token': normal_refresh_token + 'test',
            'grant_type': 'refresh_token'
        }
        admin_credentials = {
            'refresh_token': admin_refresh_token,
            'grant_type': 'refresh_token'
        }
        admin_wrong_credentials = {
            'refresh_token': admin_refresh_token + 'test',
            'grant_type': 'refresh_token'
        }
        # negative uuid invalid
        response = self.app.post('/api/auth/token', data=json.dumps(normal_wrong_credentials), content_type=content_type)
        self.assertEqual(response.status_code, 400)
        response = self.app.post('/api/auth/token', data=json.dumps(admin_wrong_credentials), content_type=content_type)
        self.assertEqual(response.status_code, 400)
        # positive
        response = self.app.post('/api/auth/token', data=json.dumps(normal_credentials), content_type=content_type)
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/api/auth/token', data=json.dumps(admin_credentials), content_type=content_type)
        self.assertEqual(response.status_code, 200)

        #revoke tokens
        response = self.app.delete('/api/auth/token?refresh_token={refresh_token}'.format(refresh_token=normal_refresh_token))
        self.assertEqual(response.status_code, 200)
        response = self.app.delete('/api/auth/token?refresh_token={refresh_token}'.format(refresh_token=normal_refresh_token))
        self.assertEqual(response.status_code, 401)
        response = self.app.delete('/api/auth/token?refresh_token={refresh_token}'.format(refresh_token=admin_refresh_token))
        self.assertEqual(response.status_code, 200)
        response = self.app.delete('/api/auth/token?refresh_token={refresh_token}'.format(refresh_token=admin_refresh_token))
        self.assertEqual(response.status_code, 401)


    def test_get_users(self):
        print('Testing Fetch Users')
        # with excess email
        admin_credentials = constants.get_admin_credentials_for_test()
        del admin_credentials['email']
        admin_credentials['grant_type'] = 'password'
        response = self.app.post('/api/auth/token', data=json.dumps(admin_credentials), content_type=content_type)
        admin_access_token = response.get_json()['data']['access_token']
        self.assertEqual(response.status_code, 200)


        # login non-admin
        credentials = {
            'username': 'juan',
            'password': 'P@ssw0rd',
            'email': 'juan@juan.com'
        }
        normal_credentials = {
            'username': 'juan',
            'password': 'P@ssw0rd',
            'grant_type': 'password'
        }
        #register
        response = self.app.post('/api/users', data=json.dumps(credentials), content_type=content_type)
        self.assertEqual(response.status_code, 200)

        # test login
        response = self.app.post('/api/auth/token', data=json.dumps(normal_credentials), content_type=content_type)
        normal_access_token = response.get_json()['data']['access_token']
        self.assertEqual(response.status_code, 200)


        # fetch users
        response = self.app.get('/api/users', data=json.dumps(normal_credentials), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 401)
        response = self.app.get('/api/users', data=json.dumps(normal_credentials), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=admin_access_token)})
        self.assertEqual(response.status_code, 200)


    def test_user_journey(self):
        print('Testing User Journey')
        # with excess email
        admin_credentials = constants.get_admin_credentials_for_test()
        del admin_credentials['email']
        admin_credentials['grant_type'] = 'password'
        response = self.app.post('/api/auth/token', data=json.dumps(admin_credentials), content_type=content_type)
        admin_access_token = response.get_json()['data']['access_token']
        self.assertEqual(response.status_code, 200)


        # login non-admin
        credentials = {
            'username': 'juan',
            'password': 'P@ssw0rd',
            'email': 'juan@juan.com'
        }
        normal_credentials = {
            'username': 'juan',
            'password': 'P@ssw0rd',
            'grant_type': 'password'
        }
        #register
        response = self.app.post('/api/users', data=json.dumps(credentials), content_type=content_type)
        self.assertEqual(response.status_code, 200)

        # test login
        response = self.app.post('/api/auth/token', data=json.dumps(normal_credentials), content_type=content_type)
        normal_access_token = response.get_json()['data']['access_token']
        self.assertEqual(response.status_code, 200)

        # fetch users
        response = self.app.get('/api/users', data=json.dumps(normal_credentials), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=admin_access_token)})
        admin_id = response.get_json()['data'][0]['id']
        user_id = response.get_json()['data'][1]['id']
        self.assertEqual(response.status_code, 200)


        # fetch lists
        response = self.app.get('/api/lists', content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/api/lists', content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=admin_access_token)})
        self.assertEqual(response.status_code, 200)


        # lists management
        list_body_unassigned = {
            "title": "Sample Title",
            "user_id": None
        }
        list_body_assigned = {
            "title": "Sample Title",
            "user_id": user_id
        }
        response = self.app.post('/api/lists', data=json.dumps(list_body_unassigned), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=admin_access_token)})
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/api/lists?id=all', headers={'Authorization': 'Bearer {access_token}'.format(access_token=admin_access_token)})
        self.assertEqual(response.status_code, 200)
        list_id = response.get_json()['data'][0]['id']
        list_body_assigned_for_update = {
            "id": list_id,
            "title": "Sample Title Updated",
            "user_id": user_id
        }
        response = self.app.put('/api/lists', data=json.dumps(list_body_assigned_for_update), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=admin_access_token)})
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/api/lists', headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()['data']), 0)


        response = self.app.delete('/api/lists?id={id}'.format(id=list_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 401)
        response = self.app.delete('/api/lists?id={id}'.format(id=list_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=admin_access_token)})
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/api/lists', headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()['data']), 0)

        # cards management
        response = self.app.post('/api/lists', data=json.dumps(list_body_assigned), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=admin_access_token)})
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/api/lists', headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)
        list_id = response.get_json()['data'][0]['id']

        card_data = {
            "title": "Sample Card Data",
            "description": "Sample Card Description",
            "list_id": list_id
        }

        card_data_update = {
            "title": "Sample Card Data Updated",
            "description": "Sample Card Description",
            "list_id": list_id
        }
        response = self.app.post('/api/cards', data=json.dumps(card_data), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/api/cards?list_id={list_id}'.format(list_id=list_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        card_id = response.get_json()['data'][0]['id']
        self.assertEqual(response.status_code, 200)

        #delete by admin
        response = self.app.delete('/api/cards?id={id}'.format(id=card_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=admin_access_token)})
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/api/cards?list_id={list_id}'.format(list_id=list_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()['data']), 0)

        # create card
        response = self.app.post('/api/cards', data=json.dumps(card_data_update), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/api/cards?list_id={list_id}'.format(list_id=list_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        card_id = response.get_json()['data'][0]['id']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['data'][0]['title'], card_data_update['title'])


        # comments management
        comments_data = {
            "card_id": card_id,
            "content": "Sample Content Comment",
            "reply_to": None
        }

        # create comment
        response = self.app.post('/api/comments', data=json.dumps(comments_data), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)

        # get comments
        response = self.app.get('/api/comments?card_id={card_id}'.format(card_id=card_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        comment_id = response.get_json()['data'][0]['id']
        self.assertEqual(response.status_code, 200)

        comments_data_update = {
            "id": comment_id,
            "content": "Sample Content Comment Updated"
        }
        #update comment
        response = self.app.put('/api/comments', data=json.dumps(comments_data_update), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)

        # get comments
        response = self.app.get('/api/comments?card_id={card_id}'.format(card_id=card_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['data'][0]['content'], comments_data_update['content'])

        comments_data_1 = {
            "card_id": card_id,
            "content": "Sample Content Reply Comment",
            "reply_to": comment_id
        }

        # create comment reply
        response = self.app.post('/api/comments', data=json.dumps(comments_data_1), content_type=content_type, headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)

        # get comments
        response = self.app.get('/api/comments?card_id={card_id}'.format(card_id=card_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()['data']), 1)

        # get comments reply
        response = self.app.get('/api/comments?card_id={card_id}&id={id}'.format(card_id=card_id, id=comment_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        reply_comment_id = response.get_json()['data'][0]['id']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()['data']), 1)

        # delete comments reply
        response = self.app.delete('/api/comments?id={id}'.format(id=reply_comment_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)

        # delete comments reply
        response = self.app.delete('/api/comments?id={id}'.format(id=comment_id), headers={'Authorization': 'Bearer {access_token}'.format(access_token=normal_access_token)})
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()