from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from extensions import db
from datetime import datetime





metadata = MetaData(schema="admin")
Base = automap_base(metadata=metadata)

def prepare_base():
    Base.prepare(db.engine, reflect=True)
    global AdminQuestionaireTemplate, AdminQuestionaireSectionTemplate, AdminQuestionaireSectionQuestionsTemplate
    AdminQuestionaireTemplate = Base.classes.admin_questionaire_templates
    AdminQuestionaireSectionTemplate = Base.classes.admin_questionaire_section_templates
    AdminQuestionaireSectionQuestionsTemplate = Base.classes.admin_questionaire_section_questions_templates

def fetch_questionaire_templates():
    data = db.session.query(AdminQuestionaireTemplate).all()
    return data

def append_questionaire_templates(data):

    #Extract Template Master Data
    Template_Data = {
        'tenant_id':data.get('tenant_id'),
        'questionaire_template_id':data.get('id'),
        'questionaire_name':data.get('TemplateName'),
        'created_by':data.get('created_by'),
        'updated_by':data.get('updated_by'),
        'status':data.get('status')
    }

    #Extract Sections
    sections = data.get('Sections')
    section_data = []

    for index, section in enumerate(sections):
        
        section_dict = {
        'questionaire_template_id': data.get('id'),
        'section_id': section.get('id'),
        'section_name': section.get('title'),
        'section_index': index,
        }

        section_data.append(section_dict)

    #Extract Questions
    questions = []
    questions_data = []
    for section in sections:
        questions.extend(section.get('questions',[]))

    for index, question in enumerate(questions):

        question_dict = {
            'section_id':question.get('section_id'),
            'question_id':question.get('id'),
            'question_type':question.get('type'),
            'question_index': index,
            'question_content':question.get('content'),
            'required':question.get('required'),
            'logical':question.get('logical'),
            'condition_value':question.get('conditional_value',None),
            'condition_type':question.get('condition_type',None),
            'parent_id':question.get('question_id',None)
        }

        questions_data.append(question_dict)

    #Extract Sub-Questions
    for question in questions:
        if question.get('logical',False) == True:
            conditional_question = question.get('conditional_question')
            if conditional_question is not None:
                conditional_sub_question = conditional_question.get('condition_sub_question')
                if conditional_sub_question is not None:
                    question_dict = {
                    'section_id':conditional_sub_question.get('section_id'),
                    'question_id':conditional_sub_question.get('id'),
                    'question_type':conditional_sub_question.get('type'),
                    'question_index': None,
                    'question_content':conditional_sub_question.get('content'),
                    'required':conditional_sub_question.get('required'),
                    'logical':conditional_sub_question.get('logical'),
                    'condition_value':conditional_question.get('condition_value',None),
                    'condition_type':conditional_question.get('condition_type',None),
                    'parent_id':conditional_sub_question.get('question_id',None)
                    }

                    questions_data.append(question_dict)
                

    # Create a new instance of the AdminQuestionaireTemplate model with the provided data
    new_template = AdminQuestionaireTemplate(**Template_Data)
    db.session.add(new_template)

    # Loop through and Create a new instance of the AdminQuestionaireSectionTemplate model with the provided data
    for section in section_data:
        new_section = AdminQuestionaireSectionTemplate(**section)
        db.session.add(new_section)

    # Loop through and Create a new instance of the  AdminQuestionaireSectionQuestionsTemplate model with the provided data
    for question in questions_data:
        new_question = AdminQuestionaireSectionQuestionsTemplate(**question)
        db.session.add(new_question)

    db.session.commit()





