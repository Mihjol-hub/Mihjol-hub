#test/test_auth.py
import json 
from tests.base import BaseTestCase
from app.models import User, Group, GroupMember, Keyword, Friendship, Notification, Post, Reaction, Comment
from app import db


class TestUserRegistration(BaseTestCase):
    def test_valid_user_registration(self):
        response = self.client.post('/register',
                                    data=json.dumps({
                                        'username': 'newuser',
                                        'email': 'newuser@example.com',
                                        'password': 'newpassword',
                                        'confirm_password': 'newpassword' #Test 12
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201) # here 200 to 201 Photo. Then test 13 Photo Assertion method
        self.assertIn('message', response.json)
        self.assertIn('User registered successfully', response.json['message'])

    def test_invalid_username_registration(self):
        # First, register a user
        self.client.post('/register',
                         data=json.dumps({
                             'username': 'testuser',
                             'email': 'testuser@example.com',
                             'password': 'testpass',
                             'confirm_password': 'testpass' #Test 12
                         }),
                         content_type='application/json')

        # Try to register with the same username
        response = self.client.post('/register',
                                    data=json.dumps({
                                        'username': 'testuser',
                                        'email': 'another@example.com',
                                        'password': 'anotherpass', 
                                        'confirm_password': 'anotherpass' #Test 12
                                    }),
                                    content_type='application/json')
        self.assert400(response)
        self.assertIn('message', response.json)
        self.assertIn('Username already exists', response.json['message'])

    def test_invalid_email_registration(self):
        response = self.client.post('/register',
                                    data=json.dumps({
                                        'username': 'newuser',
                                        'email': 'invalid-email',
                                        'password': 'newpassword'
                                    }),
                                    content_type='application/json')
        self.assert400(response)
        self.assertIn('message', response.json)
        self.assertIn('Invalid email address', response.json['message'])

    def test_mismatched_password_registration(self):
        response = self.client.post('/register',
                                    data=json.dumps({
                                        'username': 'newuser',
                                        'email': 'newuser@example.com',
                                        'password': 'password1',
                                        'confirm_password': 'password2'
                                    }),
                                    content_type='application/json')
        self.assert400(response)
        self.assertIn('message', response.json)
        self.assertIn('Passwords do not match', response.json['message'])

class TestUserLogin(BaseTestCase):
    def setUp(self):
        super().setUp()
        user = User(username='testuser', email='testuser@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    def test_valid_login(self):
        response = self.client.post('/login',
                                    data=json.dumps({
                                        'username': 'testuser',
                                        'password': 'password123'
                                    }),
                                    content_type='application/json')
        self.assert200(response)
        self.assertIn('access_token', response.json)

    def test_invalid_username(self):
        response = self.client.post('/login',
                                    data=json.dumps({
                                        'username': 'wronguser',
                                        'password': 'password123'
                                    }),
                                    content_type='application/json')
        self.assert401(response)
        self.assertIn('message', response.json)
        self.assertIn('Invalid username or password', response.json['message'])

    def test_invalid_password(self):
        response = self.client.post('/login',
                                    data=json.dumps({
                                        'username': 'testuser',
                                        'password': 'wrongpassword'
                                    }),
                                    content_type='application/json')
        self.assert401(response)
        self.assertIn('message', response.json)
        self.assertIn('Invalid username or password', response.json['message'])

    def test_logout(self):
        # First, log in to get a token
        login_response = self.client.post('/login',
                                          data=json.dumps({
                                              'username': 'testuser',
                                              'password': 'password123'
                                          }),
                                          content_type='application/json')
        token = login_response.json['access_token']

        # Now, logout using the token
        response = self.client.post('/logout',
                                    headers={'Authorization': f'Bearer {token}'},
                                    content_type='application/json')
        self.assert200(response)
        self.assertIn('msg', response.json)
        self.assertIn('Successfully logged out', response.json['msg'])

if __name__ == '__main__':
    unittest.main()