from flask import Blueprint
from app.models.admin import AdminQuestionaireTemplate, AdminQuestionaireSectionTemplate, AdminQuestionaireSectionQuestionsTemplate

bp_questionaire_templates = Blueprint('questionaire_templates', __name__, url_prefix='/questionaire_templates')

@bp_questionaire_templates.route('/')
def get_questionaire_templates():
    # Implementation for getting questionaire templates
    return 'This is the questionaire templates page.'

@bp_questionaire_templates.route('/<int:id>')
def get_questionaire_template(id):
    # Implementation for getting a specific questionaire template
    return f'This is the questionaire template with id {id}.'
