from . import db
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer  # Updated import
from flask import current_app as app


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    firstName = db.Column(db.String(30), nullable=False)
    lastName = db.Column(db.String(30), nullable=False)
    profile_picture = db.Column(db.String(200), default='default_avatar.png')  # New field
    bio = db.Column(db.Text, nullable=True)  # New field
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    messages_sent = db.relationship(
        'Messages', foreign_keys='Messages.sender_id', backref='message_sender', lazy=True
    )
    messages_received = db.relationship(
        'Messages', foreign_keys='Messages.recipient_id', backref='message_recipient', lazy=True
    )
    notifications = db.relationship('Notifications', backref='user', lazy=True)
    settings = db.relationship('Settings', backref='user', lazy=True)

    # Friends relationships
    friends = db.relationship(
        'Friends', foreign_keys='Friends.user_id', backref='user_friends', lazy=True
    )
    friend_of = db.relationship(
        'Friends', foreign_keys='Friends.friend_id', backref='friend_friends', lazy=True
    )

    # Computed property to get the number of friends
    @property
    def friend_count(self):
        # Count the number of accepted friendships
        return Friends.query.filter(
            ((Friends.user_id == self.id) | (Friends.friend_id == self.id)) &
            (Friends.status == 'accepted')
        ).count()

    # Method to generate a password reset token
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id})

    # Method to verify a password reset token
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']  # Added max_age for expiration
        except:
            return None
        return User.query.get(user_id)


class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(10), default='pending')  # 'pending', 'accepted', 'rejected'

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='friends_as_user')
    friend = db.relationship('User', foreign_keys=[friend_id], backref='friends_as_friend')

    @property
    def unread_count(self):
        return Messages.query.filter(
            Messages.sender_id == self.friend_id,
            Messages.recipient_id == self.user_id,
            Messages.is_read == False  # Assuming you have an `is_read` field in Messages
        ).count()


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)  # Add this line

    # Relationships
    sender = db.relationship(
        'User', foreign_keys=[sender_id], backref='sent_messages', overlaps="message_sender,messages_sent"
    )
    recipient = db.relationship(
        'User', foreign_keys=[recipient_id], backref='received_messages', overlaps="message_recipient,messages_received"
    )
    

class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # e.g., 'friend_request', 'message', 'like'
    is_read = db.Column(db.Boolean, default=False)  # Track if the notification has been read
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(10), default='dark')
    notifications_enabled = db.Column(db.Boolean, default=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=True)  # Path to uploaded image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='posts')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all,delete')
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all,delete')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')