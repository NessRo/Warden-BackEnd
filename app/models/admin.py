from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from extensions import db




metadata = MetaData(schema="admin")
Base = automap_base(metadata=metadata)

def prepare_base():
    Base.prepare(db.engine, reflect=True)
    global AdminQuestionaireTemplate, AdminQuestionaireSectionTemplate, AdminQuestionaireSectionQuestionsTemplate
    AdminQuestionaireTemplate = Base.classes.admin_questionaire_templates
    AdminQuestionaireSectionTemplate = Base.classes.admin_questionaire_section_templates
    AdminQuestionaireSectionQuestionsTemplate = Base.classes.admin_questionaire_section_questions_templates

def get_questionaire_templates():
    return db.session.query(AdminQuestionaireTemplate).all()

def append_questionaire_templates(data):

    sections = data.get('sections')
    questions = []
    for section in sections:
        questions.extend(section.get('questions'))
        del section['questions']


    del data['sections']

    # Create a new instance of the AdminQuestionaireTemplate model with the provided data
    new_template = AdminQuestionaireTemplate(**data)
    db.session.add(new_template)

    # Loop through and Create a new instance of the AdminQuestionaireSectionTemplate model with the provided data
    for section in sections:
        new_section = AdminQuestionaireSectionTemplate(**section)
        db.session.add(new_section)

    # Loop through and Create a new instance of the  AdminQuestionaireSectionQuestionsTemplate model with the provided data
    for question in questions:
        new_question = AdminQuestionaireSectionQuestionsTemplate(**question)
        db.session.add(new_question)

    db.session.commit()




