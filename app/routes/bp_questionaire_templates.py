from flask import Blueprint, Flask, jsonify, request,Response
import json
from app.models.admin import fetch_questionaire_templates, append_questionaire_templates


bp_questionaire_templates = Blueprint('questionaire_templates', __name__, url_prefix='/questionaire_templates')

@bp_questionaire_templates.route('/')
def get_questionaire_templates():
    # Implementation for getting questionaire templates
    
    templates = fetch_questionaire_templates()
    template_list = []
    for template in templates:
        template_list.append({
            'tenant_id':template.tenant_id,
            'questionaire_template_id':template.questionaire_template_id,
            'questionaire_name':template.questionaire_name,
            'creation_date':template.creation_date,
            'last_update_date':template.last_update_date,
            'created_by':template.created_by,
            'updated_by':template.updated_by,
            'status':template.status
        })
    
    

    return jsonify(templates=template_list)
      



@bp_questionaire_templates.route('/append', methods=['POST'])
def append_questionaire_template():
    data = request.get_json()
    if data is None:
        return jsonify(error="Invalid JSON data"), 400
    

    append_questionaire_templates(data)
    

    
    return jsonify(success=True, message="JSON data received and processed")
    
