from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required
from app.models.source import Source
from app.extensions import SessionLocal

web_sources_bp = Blueprint('web_sources_bp', __name__, template_folder='templates/sources')

@web_sources_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def list_sources():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        publication_info = request.form.get('publication_info')
        notes = request.form.get('notes')

        new_source = Source(
            title=title,
            author=author,
            publication_info=publication_info,
            notes=notes
        )
        SessionLocal.session.add(new_source)
        SessionLocal.session.commit()
        flash("Source created successfully.", "success")
        return redirect(url_for('web_sources_bp.list_sources'))

    sources = Source.query.all()
    return render_template('sources/sources_list.html', sources=sources)

@web_sources_bp.route('/<int:source_id>/delete', methods=['POST'])
@jwt_required()
def delete_source(source_id):
    source = Source.query.get_or_404(source_id)
    SessionLocal.session.delete(source)
    SessionLocal.session.commit()
    flash('Source deleted successfully.', 'success')
    return redirect(url_for('web_sources_bp.list_sources'))
