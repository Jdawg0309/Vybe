from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import User, db, Friends
import os

profile = Blueprint('profile', __name__)

@profile.route('/profile')
@login_required
def profile_view(user = current_user):
    friends = (
        db.session.query(User)
        .join(Friends, (Friends.friend_id == User.id) | (Friends.user_id == User.id))
        .filter(
            (Friends.user_id == current_user.id) | (Friends.friend_id == current_user.id),
            Friends.status == 'accepted'
        )
        .filter(User.id != current_user.id)
        .all()
    )

    pending_requests = (
        db.session.query(User, Friends)
        .join(Friends, Friends.user_id == User.id)
        .filter(Friends.friend_id == current_user.id, Friends.status == 'pending')
        .all()
    )

    if not friends:
        friends = []
    if not pending_requests:
        pending_requests = []

    return render_template('profile.html', user=user, friends=friends, pending_requests=pending_requests)

@profile.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file selected.', category='error')
        return redirect(url_for('profile.profile_view'))

    file = request.files['profile_picture']
    if file.filename == '':
        flash('No file selected.', category='error')
        return redirect(url_for('profile.profile_view'))

    # Define the upload folder path within static/images
    upload_folder = os.path.join(current_app.root_path, 'static', 'images')
    
    # Ensure upload folder exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    if file and allowed_file(file.filename):
        max_size = 5 * 1024 * 1024  # 5MB
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > max_size:
            flash('File size exceeds the limit of 5MB.', category='error')
            return redirect(url_for('profile.profile_view'))

        # Generate a unique filename to prevent collisions
        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        filepath = os.path.join(upload_folder, filename)
        
        # Save the file
        file.save(filepath)
        
        # Update user's profile picture (just store the filename, not the full path)
        current_user.profile_picture = filename
        db.session.commit()
        
        flash('Profile picture updated successfully.', category='success')
    else:
        flash('Invalid file type. Allowed types: png, jpg, jpeg, gif.', category='error')

    return redirect(url_for('profile.profile_view'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}