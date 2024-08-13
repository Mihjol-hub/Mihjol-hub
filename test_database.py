#test data_base.py
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"Total users in database: {len(users)}")
    for user in users:
        print(f"User ID: {user.id}, Username: {user.username}, Email: {user.email}")

