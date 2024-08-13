#models.py
from datetime import datetime, timezone
from passlib.context import CryptContext
from . import db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

user_keyword = db.Table('user_keyword',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('keyword_id', db.Integer, db.ForeignKey('keywords.id'), primary_key=True)
)

post_keyword = db.Table('post_keyword',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('keyword_id', db.Integer, db.ForeignKey('keywords.id'), primary_key=True)
)

group_keyword = db.Table('group_keyword',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
    db.Column('keyword_id', db.Integer, db.ForeignKey('keywords.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    workrole = db.Column(db.String(80))
    entreprise = db.Column(db.String(80))
    biography = db.Column(db.Text)
    birthday = db.Column(db.Date)
    profile_picture = db.Column(db.String(255))
    last_login = db.Column(db.DateTime)  # tracking user activities
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    keywords = db.relationship('Keyword', secondary=user_keyword, back_populates='users')
    posts = db.relationship('Post', back_populates='author')
    group_memberships = db.relationship('GroupMember', back_populates='user')
    reactions = db.relationship('Reaction', back_populates='user')
    comments = db.relationship('Comment', back_populates='author')
    sent_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.user_id', back_populates='user')
    received_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.friend_id', back_populates='friend')
    notifications = db.relationship('Notification', back_populates='user')
    created_groups = db.relationship('Group', back_populates='creator')

    def set_password(self, password):
        self.password = pwd_context.hash(password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.created_at:
            self.created_at = datetime.utcnow()

    def check_password(self, password):
        print(f"Checking password for user {self.username}")
        print(f"Stored hashed password: {self.password}")
        print(f"Provided password: {password}")
        result = pwd_context.verify(password, self.password)
        print(f"Password verification result: {result}")
        return result

    def has_permission(self, permission):
        if self.role == 'admin':
            return True
        elif permission == 'user' and self.role == 'user':
            return True
        return False

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def friends(self):
        sent_accepted = Friendship.query.filter_by(user_id=self.id, status='accepted').all()
        received_accepted = Friendship.query.filter_by(friend_id=self.id, status='accepted').all()
        friends = [relationship.friend for relationship in sent_accepted]
        friends += [relationship.user for relationship in received_accepted]
        return friends

    @property
    def pending_friend_requests(self):
        return Friendship.query.filter_by(friend_id=self.id, status='pending').all()

    @property
    def sent_requests(self):
        return Friendship.query.filter_by(user_id=self.id, status='pending').all()


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    members = db.relationship('GroupMember', back_populates='group')
    posts = db.relationship('Post', back_populates='group')
    keywords = db.relationship('Keyword', secondary='group_keyword', back_populates='groups')
    creator = db.relationship('User', back_populates='created_groups')

    def __repr__(self):
        return f'<Group {self.name}>'


class GroupMember(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='member')
    user = db.relationship('User', back_populates='group_memberships')
    group = db.relationship('Group', back_populates='members')

    def __repr__(self):
        return f'<GroupMember user_id={self.user_id} group_id={self.group_id}>'

class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('User', secondary=user_keyword, back_populates='keywords')
    posts = db.relationship('Post', secondary=post_keyword, back_populates='keywords')
    groups = db.relationship('Group', secondary='group_keyword', back_populates='keywords')

    def __repr__(self):
        return f'<Keyword {self.name}>'

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], back_populates='sent_friend_requests')
    friend = db.relationship('User', foreign_keys=[friend_id], back_populates='received_friend_requests')

    def __repr__(self):
        return f'<Friendship {self.user_id} -> {self.friend_id} ({self.status})>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # e.g., 'friend_request', 'new_comment', 'new_reaction'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}: {self.notification_type}>'

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    post_title = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    file_attachment = db.Column(db.String(255))
    visibility = db.Column(db.String(20), default='public')
    is_deleted = db.Column(db.Boolean, default=False)
    keywords = db.relationship('Keyword', secondary=post_keyword, back_populates='posts')
    author = db.relationship('User', back_populates='posts')
    group = db.relationship('Group', back_populates='posts')
    reactions = db.relationship('Reaction', back_populates='post')
    comments = db.relationship('Comment', back_populates='post')

    def __repr__(self):
        return f'<Post {self.id} by User {self.user_id}>'

class Reaction(db.Model):
    __tablename__ = 'reactions'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='reactions')
    post = db.relationship('Post', back_populates='reactions')

    def __repr__(self):
        return f'<Reaction {self.reaction_type} by User {self.user_id} on Post {self.post_id}>'

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, index=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    author = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id} on Post {self.post_id}>'


class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<TokenBlocklist {self.jti}>'

def is_token_revoked(jwt_payload):
    jti = jwt_payload['jti']
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None






