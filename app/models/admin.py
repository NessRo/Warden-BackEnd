from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy import MetaData
from extensions import db
from datetime import datetime
import uuid






metadata = MetaData(schema="admin")
Base = automap_base(metadata=metadata)

def prepare_base():
    Base.prepare(db.engine, reflect=True)
    global AdminQuestionaireTemplate, AdminQuestionaireSectionTemplate, AdminQuestionaireSectionQuestionsTemplate
    AdminQuestionaireTemplate = Base.classes.admin_questionaire_templates
    AdminQuestionaireSectionTemplate = Base.classes.admin_questionaire_section_templates
    AdminQuestionaireSectionQuestionsTemplate = Base.classes.admin_questionaire_section_questions_templates

    # Add the relationship between template and sections
    AdminQuestionaireTemplate.sections = relationship("admin_questionaire_section_templates", back_populates="template")
    AdminQuestionaireSectionTemplate.template = relationship("admin_questionaire_templates", back_populates="sections")

    # Add the relationship between sections and questions
    AdminQuestionaireSectionTemplate.questions = relationship("admin_questionaire_section_questions_templates", back_populates="section")
    AdminQuestionaireSectionQuestionsTemplate.section = relationship("admin_questionaire_section_templates", back_populates="questions")

def record_exists(template_id):
    record = db.session.query(AdminQuestionaireTemplate).filter(AdminQuestionaireTemplate.questionaire_template_id == template_id).first()
    db.session.close()
    return record is not None


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

    #check if template already exists
    if record_exists(Template_Data['questionaire_template_id']):
        transaction_type = 'update'
    else:
        transaction_type = 'append'

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
                
    try:
        if transaction_type == 'append':
    
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

        elif transaction_type == 'update':
                # Fetch and update the AdminQuestionaireTemplate record
                template = db.session.query(AdminQuestionaireTemplate).filter(AdminQuestionaireTemplate.questionaire_template_id == Template_Data['questionaire_template_id']).first()
                for key, value in Template_Data.items():
                    setattr(template, key, value)

                # Fetch all AdminQuestionaireSectionQuestionsTemplate records -- YOU HAVE TO DELETE ALL QUESTIONS FIRST IF NEEDED DURING UPDATE. SECTIONS HAVE DEPENDENCY
                all_db_questions = db.session.query(AdminQuestionaireSectionQuestionsTemplate).\
                                    join(AdminQuestionaireSectionTemplate, AdminQuestionaireSectionQuestionsTemplate.section).\
                                    join(AdminQuestionaireTemplate, AdminQuestionaireSectionTemplate.template).\
                                    filter(AdminQuestionaireTemplate.questionaire_template_id == Template_Data['questionaire_template_id']).\
                                    all()
                
                question_ids = [uuid.UUID(question['question_id']) for question in questions_data]
                db_question_ids = [question.question_id for question in all_db_questions]

                 # Fetch all AdminQuestionaireSectionTemplate records for the template ID
                all_db_sections = db.session.query(AdminQuestionaireSectionTemplate).\
                                    filter(AdminQuestionaireSectionTemplate.questionaire_template_id == Template_Data['questionaire_template_id']).\
                                    all()
                
                section_ids = [uuid.UUID(section['section_id']) for section in section_data]
                db_section_ids = [section.section_id for section in all_db_sections]
                
                
                # first append any Sections that are new and not present in the database.
                for section in section_data:
                    if uuid.UUID(section['section_id']) not in db_section_ids:
                        new_section = AdminQuestionaireSectionTemplate(**section)
                        db.session.add(new_section)


                # 2nd append any questions that are new and not present in the database. DO THIS SECOND BECAUSE QUESTIONS HAVE FORERIGN KEY DEPENDENCY ON SECTIONS TABLE.
                for question in questions_data:
                    if uuid.UUID(question['question_id']) not in db_question_ids:
                        new_question = AdminQuestionaireSectionQuestionsTemplate(**question)
                        db.session.add(new_question)
                

                # 3rd Loop through and update the Questions table. this needs to be done before we update sections in case we need to delete a questions. cant delete sections without deleting questions first.
                for db_question in all_db_questions:
                    if db_question.question_id in question_ids:
                        question = next((item for item in questions_data if uuid.UUID(item['question_id']) == db_question.question_id), None)
                        for key, value in question.items():
                            setattr(db_question, key, value)
                    else:
                        db.session.delete(db_question)

                # 4th Loop through and update the sections records
                
                for db_section in all_db_sections:
                    if db_section.section_id in section_ids:
                        section = next((item for item in section_data if uuid.UUID(item['section_id']) == db_section.section_id), None)
                        for key, value in section.items():
                            setattr(db_section, key, value)
                    else:
                        db.session.delete(db_section)
                
                db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        raise e

    finally:
        db.session.close()


    





