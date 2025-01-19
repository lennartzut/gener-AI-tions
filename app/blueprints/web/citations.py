from flask import Blueprint, render_template, request, redirect, \
    url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.citation import Citation
from app.models.source import Source
from app.extensions import SessionLocal

web_citations_bp = Blueprint('web_citations_bp', __name__)


@web_citations_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def list_citations():
    if request.method == 'POST':
        source_id = request.form.get('source_id', type=int)
        entity_type = request.form.get('entity_type')
        entity_id = request.form.get('entity_id', type=int)
        notes = request.form.get('notes')

        new_citation = Citation(
            source_id=source_id,
            entity_type=entity_type,
            entity_id=entity_id,
            notes=notes
        )
        SessionLocal.session.add(new_citation)
        SessionLocal.session.commit()
        flash("Citation created successfully.", "success")
        return redirect(url_for('web_citations_bp.list_citations'))

    citations = Citation.query.all()
    sources = Source.query.all()
    return render_template('citations/citations_list.html',
                           citations=citations, sources=sources)


@web_citations_bp.route('/<int:citation_id>/delete',
                        methods=['POST'])
@jwt_required()
def delete_citation(citation_id):
    citation = Citation.query.get_or_404(citation_id)
    SessionLocal.session.delete(citation)
    SessionLocal.session.commit()
    flash('Citation deleted successfully.', 'success')
    return redirect(url_for('web_citations_bp.list_citations'))
