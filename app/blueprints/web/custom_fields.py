from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.custom_field import CustomField
from app.extensions import SessionLocal

web_custom_fields_bp = Blueprint('web_custom_fields_bp', __name__, template_folder='templates/custom_fields')

@web_custom_fields_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def list_custom_fields():
    current_user_id = get_jwt_identity()
    if request.method == 'POST':
        table_name = request.form.get('table_name')
        field_name = request.form.get('field_name')
        field_type = request.form.get('field_type')

        new_field = CustomField(
            user_id=current_user_id,
            table_name=table_name,
            field_name=field_name,
            field_type=field_type
        )
        SessionLocal.session.add(new_field)
        SessionLocal.session.commit()
        flash("Custom field created successfully.", "success")
        return redirect(url_for('web_custom_fields_bp.list_custom_fields'))

    fields = CustomField.query.filter_by(user_id=current_user_id).all()
    return render_template('custom_fields/fields_list.html', fields=fields)
