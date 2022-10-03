from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth = Blueprint("auth", __name__)



@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password supplied.', category='error')
        else:
            flash('Incorrect email supplied.', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get("email_new")
        username = request.form.get("first_name_new")
        password1 = request.form.get("password_new")
        password2 = request.form.get("password_confirm")

        email_exists = User.query.filter_by(email=email).first()
        email_valid = re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email)
        username_valid = re.match('^[a-zA-Z0-9_-]{2,20}$', username)
        password_valid = re.match("^(?:(?=.*[a-z])(?=.*[0-9])).*$", password1)

        if email_exists:
            flash('Email is already in use.', category='error')
        elif not email_valid and len(email) < 5 :
            flash("Invalid email. Please check.", category='error')
        elif not username_valid:
            flash("Your firstname should between 2 to 8 characters and contain no special characters!", category='error')
        elif not password_valid:
            flash('Your password contain invalid characters.', category='error')
        elif len(password1) < 6:
            flash('Password is too short. Please make sure your password is between 6-10 characters.', category='error')
        elif len(password1) > 20:
            flash('Password is too long. Please make sure your password is between 6-10 characters.', category='error')
        elif password1 != password2:
            flash('Password do not match. Please try again.', category='error') 
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))

    return render_template("register.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out', category='success')
    return redirect(url_for("views.home"))



 

 
 


 
