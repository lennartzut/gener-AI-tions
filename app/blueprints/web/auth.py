from flask import (Blueprint, render_template, redirect, jsonify,
                   url_for, \
                   flash, request, make_response)
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
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data

        # Check if user already exists
        if User.query.filter((User.email == email) | (
                User.username == username)).first():
            flash('Email or username already registered.', 'error')
            return redirect(url_for('web_auth_bp.signup'))

        # Create new user with hashed password
        new_user = User(email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('web_auth_bp.login'))
    return render_template('signup.html', form=form)


@web_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Authenticate user
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Create JWT tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(
                identity=str(user.id))

            # Create response and set cookies
            response = make_response(redirect(
                url_for('web_individuals_bp.get_individuals')))
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            flash('Login successful!', 'success')
            return response
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html', form=form)


@web_auth_bp.route('/logout', methods=['GET', 'POST'])
@jwt_required()
def logout():
    response = make_response(redirect(url_for('web_auth_bp.login')))
    unset_jwt_cookies(response)
    flash('Logged out successfully.', 'success')
    return response


@web_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refreshes the access token using a valid refresh token.
    """
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(
        identity=str(current_user_id))

    response = jsonify({'message': 'Token refreshed successfully.'})
    set_access_cookies(
        response,
        new_access_token,
    )
    return response, 200
