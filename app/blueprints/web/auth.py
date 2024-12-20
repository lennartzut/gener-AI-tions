from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    make_response
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    jwt_required,
    unset_jwt_cookies,
    get_jwt_identity
)
from app.extensions import db
from app.models.user import User
from app.forms import RegistrationForm, LoginForm

web_auth_bp = Blueprint('web_auth_bp', __name__)


@web_auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data

        if User.query.filter((User.email == email) | (
                User.username == username)).first():
            flash('Email or username already in use.', 'error')
            return redirect(url_for('web_auth_bp.signup'))

        try:
            new_user = User(email=email, username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('web_auth_bp.login'))
        except Exception:
            db.session.rollback()
            flash('An error occurred during signup.', 'error')
    return render_template('auth/signup.html', form=form)


@web_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            try:
                access_token = create_access_token(
                    identity=str(user.id))
                refresh_token = create_refresh_token(
                    identity=str(user.id))

                response = make_response(redirect(
                    url_for('web_projects_bp.list_projects')))
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                flash('Login successful!', 'success')
                return response
            except Exception:
                flash('An error occurred while logging in.', 'error')
        else:
            flash('Invalid email or password.', 'error')
    return render_template('auth/login.html', form=form)


@web_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = make_response(redirect(url_for('web_auth_bp.login')))
    unset_jwt_cookies(response)
    flash('Logged out successfully.', 'success')
    return response


@web_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        response = make_response(
            {'message': 'Token refreshed successfully'})
        set_access_cookies(response, access_token)
        return response, 200
    except Exception:
        flash('An error occurred while refreshing the token.',
              'error')
        return {'error': 'Unable to refresh token'}, 500
