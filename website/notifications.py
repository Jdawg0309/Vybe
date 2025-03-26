from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from datetime import datetime
from .models import Notifications, db

# Create a Blueprint for notifications
notifications = Blueprint('notifications', __name__)

@notifications.route('/notifications')
@login_required
def notifications_view():
    """
    Route to display all notifications for the current user.
    Notifications are ordered by date (newest first).
    """
    # Fetch all notifications for the current user, ordered by date (newest first)
    notifications = Notifications.query.filter_by(user_id=current_user.id).order_by(Notifications.date.desc()).all()

    if not notifications:
        flash('No new notifications.', category='info')

    return render_template('notifications.html', user=current_user, notifications=notifications)

@notifications.route('/mark_as_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    """
    Route to mark a specific notification as read.
    """
    notification = Notifications.query.get(notification_id)

    if not notification:
        flash('Notification not found.', category='error')
    elif notification.user_id != current_user.id:
        flash('You are not authorized to mark this notification as read.', category='error')
    else:
        # Mark the notification as read
        notification.is_read = True
        db.session.commit()
        flash('Notification marked as read.', category='success')

    return redirect(url_for('notifications.notifications_view'))

@notifications.route('/mark_all_as_read', methods=['POST'])
@login_required
def mark_all_as_read():
    """
    Route to mark all notifications as read for the current user.
    """
    # Mark all unread notifications as read
    Notifications.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', category='success')
    return redirect(url_for('notifications.notifications_view'))