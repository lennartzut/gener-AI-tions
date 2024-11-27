from flask import Blueprint, jsonify, render_template, redirect, \
    url_for, flash
from extensions import db
from models.user import User
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies
)
from forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth',
                    template_folder='templates')


# Signup Route
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('auth.signup'))

        # Create and save user
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Generate JWT tokens and redirect to individuals list
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)
        response = redirect(
            url_for('web.individuals_web.get_individuals'))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        flash('Signup successful!', 'success')
        return response

    return render_template('auth/signup.html', form=form)


# Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Authenticate user
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(
                identity=str(user.id))
            response = jsonify({'login': True, 'msg': 'Login successful'})
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            flash('Login successful!', 'success')
            return response, 200
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html', form=form)


# Logout Route
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = redirect(url_for('auth.login'))
    unset_jwt_cookies(response)
    flash('Logged out successfully.', 'success')
    return response
