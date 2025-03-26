from flask import Blueprint, request, flash, redirect, url_for, current_app, jsonify, render_template
from flask_login import login_required, current_user
from .models import Post, Like, Comment, db
from datetime import datetime
from werkzeug.utils import secure_filename
import os

posts = Blueprint('posts', __name__)

@posts.route('/create_post', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content')
    image = request.files.get('image')
    
    if not content:
        flash('Post content cannot be empty', 'error')
        return redirect(url_for('profile.profile_view'))
    
    new_post = Post(
        content=content,
        user_id=current_user.id
    )

    if image and allowed_file(image.filename):
        filename = secure_filename(f"post_{datetime.now().timestamp()}.{image.filename.split('.')[-1]}")
        image.save(os.path.join(current_app.root_path, 'static', 'images', filename))
        new_post.image = filename
    
    db.session.add(new_post)
    db.session.commit()
    flash('Post created successfully!', 'success')
    return redirect(url_for('posts.posts_view'))  # Changed to redirect to posts view

@posts.route('/posts')
@login_required
def posts_view():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("posts.html", posts=posts, Comment=Comment)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@posts.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    
    if like:
        db.session.delete(like)
        action = 'unliked'
    else:
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    return jsonify({'success': True, 'action': action})

@posts.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({'success': False, 'error': 'Content is required'})
    
    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id
    )
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'content': content,
            'username': current_user.username,
            'user_id': current_user.id,
            'user_picture': current_user.profile_picture,
            'created_at': 'Just now'
        }
    })