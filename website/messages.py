from flask import Blueprint, request, flash, redirect, url_for, render_template, jsonify
from flask_login import login_required, current_user
from .models import User, Messages, Notifications, Friends, db
from datetime import datetime

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages', methods=['GET', 'POST'])
@messages_bp.route('/messages/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def messages_main(friend_id=None):
    selected_friend = None
    messages = []

    if request.method == 'POST':
        recipient_username = request.form.get('recipient_username')
        message_content = request.form.get('message_content')

        # If sending to a specific friend (from chat view)
        if friend_id:
            recipient = User.query.get(friend_id)
            if not recipient:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify(success=False, error='Friend not found.')
                flash('Friend not found.', category='error')
                return redirect(url_for('messages.messages_main'))
        else:
            # If sending to any user (from main messages view)
            recipient = User.query.filter_by(username=recipient_username).first()
            if not recipient:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify(success=False, error='User not found.')
                flash('User not found.', category='error')
                return redirect(url_for('messages.messages_main'))

        if not message_content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(success=False, error='Message cannot be empty.')
            flash('Message cannot be empty.', category='error')
            return redirect(url_for('messages.messages_main'))

        new_message = Messages(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            message_content=message_content,
            is_read=False
        )
        db.session.add(new_message)
        db.session.commit()

        notification = Notifications(
            user_id=recipient.id,
            notification_content=f"{current_user.username} sent you a message.",
            notification_type='message',
            is_read=False,
            date=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(
                success=True,
                message_content=message_content,
                recipient_username=recipient.username
            )

        flash('Message sent successfully.', category='success')
        if friend_id:
            return redirect(url_for('messages.messages_main', friend_id=friend_id))
        else:
            return redirect(url_for('messages.messages_main'))

    if friend_id:
        selected_friend = User.query.get(friend_id)
        if not selected_friend:
            flash('Friend not found.', category='error')
            return redirect(url_for('messages.messages_main'))

        messages = Messages.query.filter(
            ((Messages.sender_id == current_user.id) & (Messages.recipient_id == selected_friend.id)) |
            ((Messages.sender_id == selected_friend.id) & (Messages.recipient_id == current_user.id))
        ).order_by(Messages.date.asc()).all()
        
        # Mark messages as read when viewing conversation
        Messages.query.filter_by(recipient_id=current_user.id, sender_id=selected_friend.id, is_read=False).update({'is_read': True})
        db.session.commit()
    else:
        messages = Messages.query.filter(
            (Messages.sender_id == current_user.id) | (Messages.recipient_id == current_user.id)
        ).order_by(Messages.date.desc()).all()

    # Get friends with unread counts
    friends_with_unread = []
    friendships = Friends.query.filter(
        ((Friends.user_id == current_user.id) | (Friends.friend_id == current_user.id)) &
        (Friends.status == 'accepted')
    ).all()

    for friendship in friendships:
        friend = friendship.friend if friendship.user_id == current_user.id else friendship.user
        unread_count = Messages.query.filter(
            Messages.sender_id == friend.id,
            Messages.recipient_id == current_user.id,
            Messages.is_read == False
        ).count()
        
        friends_with_unread.append({
            'friend': friend,
            'unread_count': unread_count
        })

    return render_template(
        'messages.html',
        user=current_user,
        selected_friend=selected_friend,
        messages=messages,
        friends_with_unread=friends_with_unread
    )

@messages_bp.route('/react_to_message/<int:message_id>', methods=['POST'])
@login_required
def react_to_message(message_id):
    message = Messages.query.get(message_id)
    if not message:
        return jsonify(success=False, error='Message not found.')

    reaction = request.json.get('reaction')
    if not reaction or reaction not in ['👍', '❤️', '😄']:
        return jsonify(success=False, error='Invalid reaction.')

    if not message.reactions:
        message.reactions = []
    message.reactions.append(reaction)
    db.session.commit()

    return jsonify(success=True)

@messages_bp.route('/edit_message/<int:message_id>', methods=['POST'])
@login_required
def edit_message(message_id):
    message = Messages.query.get(message_id)
    if not message:
        return jsonify(success=False, error='Message not found.')

    if message.sender_id != current_user.id:
        return jsonify(success=False, error='You are not authorized to edit this message.')

    new_content = request.json.get('new_content')
    if not new_content or new_content.strip() == '':
        return jsonify(success=False, error='Message content cannot be empty.')

    message.message_content = new_content
    db.session.commit()

    return jsonify(success=True)

@messages_bp.route('/delete_message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    message = Messages.query.get(message_id)
    if not message:
        return jsonify(success=False, error='Message not found.')

    if message.sender_id != current_user.id:
        return jsonify(success=False, error='You are not authorized to delete this message.')

    db.session.delete(message)
    db.session.commit()

    return jsonify(success=True)

@messages_bp.route('/pin_message/<int:message_id>', methods=['POST'])
@login_required
def pin_message(message_id):
    message = Messages.query.get(message_id)
    if not message:
        return jsonify(success=False, error='Message not found.')

    message.is_pinned = True
    db.session.commit()

    return jsonify(success=True)