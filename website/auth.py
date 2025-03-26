from flask import Blueprint, request, flash, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from .models import User, db

auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
        return render_template('home.html')

@auth.route('/settings')
def settings():
    return render_template("settings.html")

@auth.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        firstName = request.form.get("firstname")
        lastName = request.form.get("lastname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")

        errors = []

        if not firstName or len(firstName) < 2:
            errors.append("First name must be at least 2 characters long.")
        if not lastName or len(lastName) < 2:
            errors.append("Last name must be at least 2 characters long.")
        if not username or len(username) < 4:
            errors.append("Username must be at least 4 characters long.")
        if not email or "@" not in email:
            errors.append("Invalid email address.")
        if not password or len(password) < 7:
            errors.append("Password must be at least 7 characters long.")
        if password != confirmPassword:
            errors.append("Passwords do not match.")

        user = User.query.filter_by(username=username).first()
        if user:
            errors.append("Username is already taken.")
        user = User.query.filter_by(email=email).first()
        if user:
            errors.append("Email is already registered.")

        if errors:
            for error in errors:
                flash(error, category='error')
        else:
            new_user = User(
                firstName=firstName,
                lastName=lastName,
                username=username,
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('profile.profile_view'))

    return render_template('signup.html')

@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash('Please fill in all fields.', category='error')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User does not exist.', category='error')
        elif not check_password_hash(user.password, password):
            flash('Incorrect password. Please try again.', category='error')
        else:
            login_user(user, remember=True)
            flash('Login successful!', category='success')
            return redirect(url_for('profile.profile_view'))

    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', category='success')
    return redirect(url_for('auth.home'))

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Password reset instructions sent to your email.', category='success')
        else:
            flash('Email not found.', category='error')
        return redirect(url_for('auth.forgot_password'))

    return render_template('forgot_password.html')

@auth.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Validate inputs
        if not old_password or not new_password or not confirm_password:
            flash('Please fill in all fields', category='error')
            return redirect(url_for('auth.settings'))

        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match', category='error')
            return redirect(url_for('auth.settings'))

        # Check if new password is different from old
        if old_password == new_password:
            flash('New password must be different from old password', category='error')
            return redirect(url_for('auth.settings'))

        # Verify old password
        if not check_password_hash(current_user.password, old_password):
            flash('Incorrect current password', category='error')
            return redirect(url_for('auth.settings'))

        # Check password strength
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', category='error')
            return redirect(url_for('auth.settings'))

        # Update password
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()

        flash('Password changed successfully!', category='success')
        return redirect(url_for('auth.settings'))

    return redirect(url_for('auth.settings'))


@auth.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    if request.method == "POST":
        # Get the current user
        user = current_user
        
        # Logout the user first
        logout_user()
        
        # Delete the user from database
        db.session.delete(user)
        db.session.commit()
        
        flash('Your account has been successfully deleted', category='success')
        return redirect(url_for('auth.home'))
    
    return redirect(url_for('auth.settings'))