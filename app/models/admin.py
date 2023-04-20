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

def print_table_names():
       for key, value in Base.classes.items():
        print(f"{key} => {value}")



# Assign the mapped classes to variables
AdminQuestionaireTemplate = None
AdminQuestionaireSectionTemplate = None
AdminQuestionaireSectionQuestionsTemplate = None



