from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Friends, Notifications, db
from datetime import datetime

friends = Blueprint('friends', __name__)

@friends.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    friend_username = request.form.get('friend_username')
    friend = User.query.filter_by(username=friend_username).first()

    if not friend:
        flash('User not found.', category='error')
    elif friend.id == current_user.id:
        flash('You cannot add yourself as a friend.', category='error')
    else:
        existing_friendship = Friends.query.filter_by(user_id=current_user.id, friend_id=friend.id).first()
        if existing_friendship:
            flash('Friend request already sent or accepted.', category='error')
        else:
            new_friendship = Friends(user_id=current_user.id, friend_id=friend.id, status='pending')
            db.session.add(new_friendship)

            notification = Notifications(
                user_id=friend.id,
                notification_content=f"{current_user.username} sent you a friend request.",
                notification_type='friend_request',
                is_read=False,
                date=datetime.utcnow()
            )
            db.session.add(notification)
            db.session.commit()

            flash('Friend request sent.', category='success')

    return redirect(url_for('profile.profile_view'))

@friends.route('/accept_friend', methods=['POST'])
@login_required
def accept_friend():
    request_id = request.form.get('request_id')
    friendship = Friends.query.get(request_id)

    if not friendship:
        flash('Friend request not found.', category='error')
    elif friendship.friend_id != current_user.id:
        flash('You are not authorized to accept this request.', category='error')
    else:
        friendship.status = 'accepted'
        db.session.commit()

        notification = Notifications(
            user_id=friendship.user_id,
            notification_content=f"{current_user.username} accepted your friend request.",
            notification_type='friend_request_accepted',
            is_read=False,
            date=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()

        flash('Friend request accepted.', category='success')

    return redirect(url_for('profile.profile_view'))

@friends.route('/reject_friend', methods=['POST'])
@login_required
def reject_friend():
    request_id = request.form.get('request_id')
    friendship = Friends.query.get(request_id)

    if not friendship:
        flash('Friend request not found.', category='error')
    elif friendship.friend_id != current_user.id:
        flash('You are not authorized to reject this request.', category='error')
    else:
        db.session.delete(friendship)

        notification = Notifications(
            user_id=friendship.user_id,
            notification_content=f"{current_user.username} rejected your friend request.",
            notification_type='friend_request_rejected',
            is_read=False,
            date=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()

        flash('Friend request rejected.', category='success')

    return redirect(url_for('profile.profile_view'))

@friends.route('/remove_friend', methods=['POST'])
@login_required
def remove_friend():
    friend_id = request.form.get('friend_id')
    friend = User.query.get(friend_id)

    if not friend:
        flash('Friend not found.', category='error')
    else:
        friendship = Friends.query.filter(
            ((Friends.user_id == current_user.id) & (Friends.friend_id == friend.id)) |
            ((Friends.user_id == friend.id) & (Friends.friend_id == current_user.id))
        ).first()

        if not friendship:
            flash('Friendship not found.', category='error')
        else:
            db.session.delete(friendship)

            notification = Notifications(
                user_id=friend.id,
                notification_content=f"{current_user.username} removed you from their friends list.",
                notification_type='friend_removed',
                is_read=False,
                date=datetime.utcnow()
            )
            db.session.add(notification)
            db.session.commit()

            flash('Friend removed successfully.', category='success')

    return redirect(url_for('profile.profile_view'))