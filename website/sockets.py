from flask_socketio import emit, join_room  # Added join_room import
from .models import Messages, db
from flask_login import current_user
from datetime import datetime
from . import socketio

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')  # Now join_room is defined
        emit('connected', {'message': f'User {current_user.username} connected'})

@socketio.on('send_message')
def handle_send_message(data):
    if not current_user.is_authenticated:
        return
    
    recipient_id = data.get('recipient_id')
    message_content = data.get('message_content')
    
    if not recipient_id or not message_content:
        return
    
    new_message = Messages(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        message_content=message_content,
        is_read=False,
        date=datetime.utcnow()
    )
    db.session.add(new_message)
    db.session.commit()
    
    # Broadcast the new message to the recipient
    emit('new_message', {
        'sender_id': current_user.id,
        'recipient_id': recipient_id,
        'message_content': message_content,
        'date': datetime.utcnow().isoformat(),
        'sender_username': current_user.username
    }, room=f'user_{recipient_id}')
    
    # Also send to sender (for their own UI update)
    emit('new_message', {
        'sender_id': current_user.id,
        'recipient_id': recipient_id,
        'message_content': message_content,
        'date': datetime.utcnow().isoformat(),
        'sender_username': current_user.username
    }, room=f'user_{current_user.id}')

# Removed the separate 'join' handler since we're joining on connect