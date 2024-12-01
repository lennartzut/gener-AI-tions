from flask import Blueprint, render_template

web_main_bp = Blueprint(
    'web_main_bp',
    __name__,
    template_folder='templates/main',
)


@web_main_bp.route('/', methods=['GET'])
def home():
    return render_template('main.html')