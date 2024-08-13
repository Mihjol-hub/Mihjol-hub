#tests/base.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_testing import TestCase
from app import create_app, db
from config import TestingConfig

class BaseTestCase(TestCase):
    def create_app(self):
        # Use TestingConfig but override the database URI
        app = create_app('testing')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()