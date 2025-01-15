from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, make_response, request, jsonify
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
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import SessionLocal
from app.schemas.user_schema import UserCreate, UserLogin
from app.services.user_service import UserService, UserAlreadyExistsError

web_auth_bp = Blueprint('web_auth_bp', __name__,
                        template_folder='templates/auth')


@web_auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            form_data = request.form.to_dict()
            user_create = UserCreate.model_validate(form_data)
        except Exception as e:
            flash(f"Validation error: {e}", 'danger')
            return render_template('auth/signup.html', form_data=form_data)

        try:
            with SessionLocal() as session:
                service = UserService(db=session)
                new_user = service.create_user(user_create=user_create)
                if new_user:
                    flash('Signup successful! Please log in.', 'success')
                    return redirect(url_for('web_auth_bp.login'))
                flash('Email or username already in use.', 'danger')
        except UserAlreadyExistsError as e:
            flash(str(e), 'danger')
        except SQLAlchemyError as e:
            flash(f"Database error: {e}", 'danger')
        except Exception as e:
            flash(f"Unexpected error: {e}", 'danger')

        return render_template('auth/signup.html', form_data=form_data)

    return render_template('auth/signup.html')


@web_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            form_data = request.form.to_dict()
            user_login = UserLogin.model_validate(form_data)
        except Exception as e:
            flash(f"Validation error: {e}", 'danger')
            return render_template('auth/login.html', form_data=form_data)

        try:
            with SessionLocal() as session:
                service = UserService(db=session)
                user = service.authenticate_user(
                    email=user_login.email,
                    password=user_login.password
                )
                if user:
                    access_token = create_access_token(identity=str(user.id))
                    refresh_token = create_refresh_token(identity=str(user.id))

                    response = make_response(
                        redirect(url_for('web_projects_bp.list_projects'))
                    )
                    set_access_cookies(response, access_token)
                    set_refresh_cookies(response, refresh_token)
                    flash('Login successful!', 'success')
                    return response
                flash('Invalid email or password.', 'danger')
        except SQLAlchemyError as e:
            flash(f"Database error: {e}", 'danger')
        except Exception as e:
            flash(f"Login error: {e}", 'danger')

        return render_template('auth/login.html', form_data=form_data)

    return render_template('auth/login.html')


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
        if not user_id:
            flash('No user identity in token.', 'danger')
            return redirect(url_for('web_auth_bp.login'))

        access_token = create_access_token(identity=user_id)
        response = make_response(
            redirect(url_for('web_projects_bp.list_projects'))
        )
        set_access_cookies(response, access_token)
        flash('Token refreshed successfully.', 'success')
        return response
    except Exception as e:
        flash(f"Token refresh error: {e}", 'danger')
        return redirect(url_for('web_auth_bp.login'))
