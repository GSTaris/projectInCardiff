import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db

upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'static/images')
print('upload_dir: {}'.format(upload_dir))
views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get('title')
        description = request.form.get('description')
        text = request.form.get('text')

        upload_file = request.files['image']
        filename = 'default.jpg'
        if upload_file:
            filename = upload_file.filename
            upload_file.save(os.path.join(upload_dir, filename))
            
        if not title:
            flash('title cannot be empty', category='error')
        elif not description:
            flash('description cannot be empty', category='error')
        elif not text:
            flash('text cannot be empty', category='error')
        else:
            post = Post(title=title, description=description, text=text, author=current_user.id, image_file=filename)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.user.id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')
    star = request.form.get('star') or 0
    print('star: {}'.format(star))
    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        
        if post:
            comment = Comment(
                text=text, star=star, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})


@views.route("/post/<post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('post.html',title=post.title, description=post.description, post=post, user=current_user)

@views.route("/pers-greet")
def pers_greet():
    return render_template("pers_greet.html", user=current_user)


@views.route("/create-comment-post/<post_id>", methods=['POST'])
@login_required
def create_comment_post(post_id):
    text = request.form.get('text')
    star = request.form.get('star') or 0

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, star=star, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')
        return redirect(request.referrer)

@views.route("/delete-comment-post/<comment_id>")
@login_required
def delete_comment_post(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(request.referrer)



