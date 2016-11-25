from django.conf import settings
from formpack import FormPack
from onadata.apps.fsforms.models import FieldsightInstance, FieldSightXF
from onadata.apps.viewer.models.parsed_instance import dict_for_mongo, _encode_for_mongo, xform_instances


def get_instances_for_field_sight_form(fieldsight_form_id, submission=None):

    # instance_id = FieldsightInstance.objects.filter(fsxform__id=fieldsight_form_id)[0].instance.id\
    #     if FieldsightInstance.objects.filter(fsxform__id=fieldsight_form_id).exists() else None

    query = {'_uuid': fieldsight_form_id, '_deleted_at': {'$exists': False}}
    if submission:
        query['_id'] = submission
    return settings.MONGO_DB.instances.find(query)


def get_instance_form_data(fieldsight_form_id, instance_id):

    query = {'_id': instance_id, '_deleted_at': {'$exists': False}}
    return settings.MONGO_DB.instances.find(query)


def build_formpack(id_string, xform):
    schema = {
        "id_string": id_string,
        "version": 'v1',
        "content": xform.to_kpi_content_schema(),
    }
    return  xform, FormPack([schema], xform.title)


def build_export_context(request,xform, id_string):

    hierarchy_in_labels = request.REQUEST.get('hierarchy_in_labels', None)
    group_sep = request.REQUEST.get('group_sep', '/')

    xform, formpack = build_formpack(id_string, xform)

    translations = formpack.available_translations
    lang = request.REQUEST.get('lang', None) or next(iter(translations), None)

    options = {'versions': 'v1',
               'group_sep': group_sep,
               'lang': lang,
               'hierarchy_in_labels': hierarchy_in_labels,
               # 'copy_fields': ('_id', '_uuid', '_submission_time''),
               'copy_fields': ('_id','_submission_time','medias'),
               # 'force_index': True
               'force_index': False
               }

    return {
        'id_string': id_string,
        'languages': translations,
        'headers_lang': lang,
        'formpack': formpack,
        'xform': xform,
        'group_sep': group_sep,
        'lang': lang,
        'hierarchy_in_labels': hierarchy_in_labels,
        'export': formpack.export(**options)
    }



def get_xform_and_perms(fsxf_id, request):
    fs_xform = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fs_xform.xf
    is_owner = xform.user == request.user
    can_edit = True
    can_view = can_edit or\
        request.user.has_perm('logger.view_xform', xform)
    return [xform, is_owner, can_edit, can_view]

import json
from bson import json_util
from onadata.libs.utils.decorators import apply_form_field_names
DEFAULT_LIMIT = 30000



@apply_form_field_names
def query_mongo(username, id_string, query, fields, sort, start=0,
                    limit=DEFAULT_LIMIT, count=False, hide_deleted=True, fsxfid=None):
    USERFORM_ID = u'_userform_id'
    STATUS = u'_status'
    DEFAULT_BATCHSIZE = 1000

    fields_to_select = {USERFORM_ID: 0}
    # TODO: give more detailed error messages to 3rd parties
    # using the API when json.loads fails
    if isinstance(query, basestring):
        query = json.loads(query, object_hook=json_util.object_hook)
    query = query if query else {}
    query = dict_for_mongo(query)
    query[USERFORM_ID] = u'%s_%s' % (username, id_string)

    # check if query contains and _id and if its a valid ObjectID
    # if '_uuid' in query and ObjectId.is_valid(query['_uuid']):
    #     query['_uuid'] = ObjectId(query['_uuid'])

    if fsxfid is not None:
        query.pop('_userform_id')
        query['_uuid'] = fsxfid
    if hide_deleted:
        # display only active elements
        # join existing query with deleted_at_query on an $and
        query = {"$and": [query, {"_deleted_at": None}]}

    # fields must be a string array i.e. '["name", "age"]'
    if isinstance(fields, basestring):
        fields = json.loads(fields, object_hook=json_util.object_hook)
    fields = fields if fields else []

    # TODO: current mongo (2.0.4 of this writing)
    # cant mix including and excluding fields in a single query
    if type(fields) == list and len(fields) > 0:
        fields_to_select = dict(
            [(_encode_for_mongo(field), 1) for field in fields])
    if isinstance(sort, basestring):
        sort = json.loads(sort, object_hook=json_util.object_hook)
    sort = sort if sort else {}

    cursor = xform_instances.find(query, fields_to_select)
    if count:
        return [{"count": cursor.count()}]

    if start < 0 or limit < 0:
        raise ValueError(_("Invalid start/limit params"))

    cursor.skip(start).limit(limit)
    if type(sort) == dict and len(sort) == 1:
        sort_key = sort.keys()[0]
        # TODO: encode sort key if it has dots
        sort_dir = int(sort[sort_key])  # -1 for desc, 1 for asc
        cursor.sort(_encode_for_mongo(sort_key), sort_dir)
    # set batch size
    cursor.batch_size = DEFAULT_BATCHSIZE
    return cursor
