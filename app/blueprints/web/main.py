from flask import Blueprint, render_template

web_main_bp = Blueprint(
    'web_main_bp',
    __name__,
    template_folder='templates/main'
)


@web_main_bp.route('/', methods=['GET'])
def home():
    """
    Renders the home page.
    """
    return render_template('main.html')


@web_main_bp.route('/templates/partials/forms/identity_form.html')
def identity_form():
    """
    Serves the identity form partial template.
    """
    return render_template('partials/forms/identity_form.html')
