from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app as app, abort
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from datetime import datetime, date
from typing import Optional
from app.extensions import db
from app.models.individual import Individual
from app.models.identity import Identity
from app.models.enums import GenderEnum
from app.models.project import Project
from app.models.family import Family
from app.utils.family_utils import get_family_by_parents, add_relationship_for_new_individual

web_individuals_bp = Blueprint('web_individuals_bp', __name__)

def parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            app.logger.error(f"Invalid date format: {date_str}")
    return None

def get_project_or_404(user_id: int, project_id: int):
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        abort(404, description="Project not found or not owned by this user.")
    return project

@web_individuals_bp.route('/', methods=['GET'])
@jwt_required()
def get_individuals():
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    individual_id = request.args.get('individual_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))

    get_project_or_404(current_user_id, project_id)

    search_query = request.args.get('q', '').strip()
    query = Individual.query.filter_by(user_id=current_user_id, project_id=project_id).options(joinedload(Individual.identities))

    if search_query:
        query = query.join(Identity).filter(
            (Identity.first_name.ilike(f'%{search_query}%')) |
            (Identity.last_name.ilike(f'%{search_query}%')) |
            (Individual.birth_place.ilike(f'%{search_query}%'))
        )

    individuals_list = query.order_by(Individual.updated_at.desc()).all()

    selected_individual = None
    selected_identity = None
    selected_individual_age = None
    parents = []
    siblings = []
    partners = []
    children = []
    parent_family = None
    selected_partner_family = None

    if individual_id:
        selected_individual = Individual.query.filter_by(
            id=individual_id, user_id=current_user_id, project_id=project_id
        ).options(joinedload(Individual.identities)).first()

        if selected_individual:
            selected_identity = selected_individual.primary_identity
            if selected_individual.birth_date:
                today = selected_individual.death_date or date.today()
                selected_individual_age = (
                        today.year - selected_individual.birth_date.year -
                        ((today.month, today.day) < (
                        selected_individual.birth_date.month,
                        selected_individual.birth_date.day))
                )
            parents = selected_individual.get_parents() if hasattr(selected_individual, 'get_parents') else []
            siblings = selected_individual.get_siblings() if hasattr(selected_individual, 'get_siblings') else []
            partners = selected_individual.get_partners() if hasattr(selected_individual, 'get_partners') else []

            selected_partner_id = request.args.get('partner_id', type=int)
            if partners and selected_partner_id:
                selected_partner = next((p for p in partners if p.id == selected_partner_id), None)
            else:
                selected_partner = partners[0] if partners else None

            if selected_partner:
                children = selected_individual.get_children(partner_id=selected_partner.id) if hasattr(selected_individual, 'get_children') else []
                selected_partner_family = get_family_by_parents(selected_individual.id, selected_partner.id, project_id)
            else:
                children = selected_individual.get_children() if hasattr(selected_individual, 'get_children') else []

            if parents:
                parent_family = Family.query.filter(
                    Family.project_id == project_id,
                    Family.children.contains(selected_individual),
                    ((Family.partner1_id.in_([p.id for p in parents])) | (Family.partner2_id.in_([p.id for p in parents])))
                ).first()

    return render_template(
        'projects/project_page.html',
        project_id=project_id,
        individuals_list=individuals_list,
        selected_individual=selected_individual,
        selected_identity=selected_identity,
        selected_individual_age=selected_individual_age,
        parents=parents,
        siblings=siblings,
        partners=partners,
        children=children,
        parent_family=parent_family,
        selected_partner_family=selected_partner_family,
        GenderEnum=GenderEnum
    )


@web_individuals_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create_individual():
    """
    CREATE Individual:
    Render a form to create a new individual.
    On POST, create the individual and a default identity, and handle optional relationship.
    """
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))

    get_project_or_404(current_user_id, project_id)

    if request.method == 'POST':
        birth_date = parse_date(request.form.get('birth_date'))
        birth_place = request.form.get('birth_place') or None
        death_date = parse_date(request.form.get('death_date'))
        death_place = request.form.get('death_place') or None
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender_str = request.form.get('gender')
        relationship = request.form.get('relationship')
        related_individual_id = request.form.get('related_individual_id', type=int)
        family_id = request.form.get('family_id', type=int)

        if not first_name or not last_name or not gender_str:
            flash("First name, last name, and gender are required.", 'error')
            return redirect(url_for('web_individuals_bp.create_individual', project_id=project_id))

        try:
            gender = GenderEnum(gender_str)

            new_individual = Individual(
                user_id=current_user_id,
                project_id=project_id,
                birth_date=birth_date,
                birth_place=birth_place,
                death_date=death_date,
                death_place=death_place
            )
            db.session.add(new_individual)
            db.session.flush()

            from app.models.identity import Identity
            default_identity = Identity(
                individual_id=new_individual.id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                valid_from=birth_date
            )
            db.session.add(default_identity)

            if relationship and (related_individual_id or family_id):
                add_relationship_for_new_individual(
                    relationship=relationship,
                    related_individual_id=related_individual_id,
                    new_individual=new_individual,
                    family_id=family_id,
                    user_id=current_user_id
                )

            db.session.commit()
            flash('Individual and default identity created successfully.', 'success')
            return redirect(url_for('web_individuals_bp.get_individuals', project_id=project_id))

        except ValueError as e:
            db.session.rollback()
            flash(f"Invalid input: {e}", 'error')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating individual: {e}")
            flash('An error occurred while creating the individual.', 'error')

    # Render a modal or a form page to create an individual
    return render_template('partials/modals/create_individual_modal.html', GenderEnum=GenderEnum, project_id=project_id)


@web_individuals_bp.route('/<int:individual_id>/update', methods=['GET', 'POST'])
@jwt_required()
def update_individual(individual_id):
    """
    UPDATE Individual:
    Render a form to update individual data.
    On POST, update the individual's details.
    """
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))

    get_project_or_404(current_user_id, project_id)

    individual = Individual.query.filter_by(
        id=individual_id, user_id=current_user_id, project_id=project_id
    ).first_or_404()

    if request.method == 'POST':
        birth_date = parse_date(request.form.get('birth_date'))
        birth_place = request.form.get('birth_place') or None
        death_date = parse_date(request.form.get('death_date'))
        death_place = request.form.get('death_place') or None
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender_str = request.form.get('gender')
        relationship = request.form.get('relationship')
        related_individual_id = request.form.get('related_individual_id', type=int)
        family_id = request.form.get('family_id', type=int)

        try:
            individual.birth_date = birth_date
            individual.birth_place = birth_place
            individual.death_date = death_date
            individual.death_place = death_place

            primary_identity = individual.primary_identity
            if primary_identity:
                primary_identity.first_name = first_name
                primary_identity.last_name = last_name
                primary_identity.gender = GenderEnum(gender_str)

            if relationship and (related_individual_id or family_id):
                add_relationship_for_new_individual(
                    relationship=relationship,
                    related_individual_id=related_individual_id,
                    new_individual=individual,
                    family_id=family_id,
                    user_id=current_user_id
                )

            db.session.commit()
            flash('Individual updated successfully.', 'success')
            return redirect(url_for('web_individuals_bp.get_individuals', project_id=project_id, individual_id=individual_id))

        except ValueError as e:
            db.session.rollback()
            flash(f"Invalid input: {e}", 'error')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating individual: {e}")
            flash('An error occurred while updating the individual.', 'danger')

    selected_gender = individual.primary_identity.gender if individual.primary_identity else None
    return render_template('partials/modals/update_individual_modal.html',
                           GenderEnum=GenderEnum,
                           selected_gender=selected_gender,
                           individual=individual,
                           project_id=project_id)


@web_individuals_bp.route('/<int:individual_id>/delete', methods=['POST'])
@jwt_required()
def delete_individual(individual_id: int):
    """
    DELETE Individual:
    Delete an individual and redirect back to the project page.
    """
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))

    get_project_or_404(current_user_id, project_id)

    individual = Individual.query.filter_by(
        id=individual_id, user_id=current_user_id, project_id=project_id
    ).first_or_404()

    try:
        db.session.delete(individual)
        db.session.commit()
        flash('Individual deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting individual: {e}")
        flash('An error occurred while deleting the individual.', 'error')

    return redirect(url_for('web_individuals_bp.get_individuals', project_id=project_id))
