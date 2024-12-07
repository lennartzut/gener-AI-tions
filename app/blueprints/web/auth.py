from flask import (
    Blueprint, render_template, redirect, jsonify,
    url_for, flash, current_app, make_response
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies
)
from app.models.user import User
from app.extensions import db, bcrypt
from app.forms import RegistrationForm, LoginForm

web_auth_bp = Blueprint(
    'web_auth_bp',
    __name__,
    template_folder='templates/auth'
)


@web_auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handles user registration.

    GET: Renders the signup form.
    POST: Validates and registers a new user with unique email and username.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data

        # Check for existing user
        if User.query.filter((User.email == email) | (
                User.username == username)).first():
            flash('Email or username already registered.', 'error')
            return redirect(url_for('web_auth_bp.signup'))

        try:
            # Create new user
            new_user = User(email=email, username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('web_auth_bp.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Signup error: {e}")
            flash('An error occurred during signup.', 'error')

    return render_template('signup.html', form=form)


@web_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.

    GET: Renders the login form.
    POST: Authenticates user and sets JWT tokens in cookies.
    """
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            try:
                # Generate tokens and set cookies
                response = make_response(redirect(
                    url_for('web_individuals_bp.get_individuals')))
                set_access_cookies(response, create_access_token(
                    identity=(user.id)))
                set_refresh_cookies(response, create_refresh_token(
                    identity=(user.id)))
                flash('Login successful!', 'success')
                return response
            except Exception as e:
                current_app.logger.error(f"Login error: {e}")
                flash('An error occurred while logging in.', 'error')

        flash('Invalid email or password.', 'error')

    return render_template('login.html', form=form)


@web_auth_bp.route('/logout', methods=['GET', 'POST'])
@jwt_required()
def logout():
    """
    Logs the user out by clearing JWT cookies.
    """
    response = make_response(redirect(url_for('web_auth_bp.login')))
    unset_jwt_cookies(response)
    flash('Logged out successfully.', 'success')
    return response


@web_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refreshes access token using a valid refresh token.
    """
    try:
        response = jsonify(
            {'message': 'Token refreshed successfully.'})
        set_access_cookies(response, create_access_token(
            identity=int(get_jwt_identity())))
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Unable to refresh token.'}), 500
