import json
from django.conf import settings

def get_multiple_options_count(fs_project, fs_project_form_uuid, question_name):
    try:
        return settings.MONGO_DB.instances.aggregate([ { "$match" : { "fs_project" : int(fs_project), "fs_project_uuid" : str(fs_project_form_uuid) } }, { "$group": { "_id": "$"+str(question_name),  "value": { "$sum": 1 } }}, { "$project": { "_id": 0, "name": "$_id", "value": 1, }} ])
    except:
        return {'status':"failed"}