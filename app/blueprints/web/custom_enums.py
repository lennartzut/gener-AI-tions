from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.custom_enum import CustomEnum
from app.extensions import SessionLocal

web_custom_enums_bp = Blueprint('web_custom_enums_bp', __name__, template_folder='templates/custom_enums')

@web_custom_enums_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def list_custom_enums():
    current_user_id = get_jwt_identity()
    if request.method == 'POST':
        enum_name = request.form.get('enum_name')
        enum_value = request.form.get('enum_value')

        new_enum = CustomEnum(
            user_id=current_user_id,
            enum_name=enum_name,
            enum_value=enum_value
        )
        SessionLocal.session.add(new_enum)
        SessionLocal.session.commit()
        flash("Custom enum value created successfully.", "success")
        return redirect(url_for('web_custom_enums_bp.list_custom_enums'))

    enums = CustomEnum.query.filter_by(user_id=current_user_id).all()
    return render_template('custom_enums/enums_list.html', enums=enums)
