from flask import Blueprint, render_template

main_web_bp = Blueprint('main_web', __name__,
                        template_folder='templates')


@main_web_bp.route('/', methods=['GET'])
def home():
    return render_template('main.html')
