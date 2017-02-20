from django.conf.urls import url, include
from rest_framework import routers

from onadata.apps.fsforms.viewsets.FieldSightXformViewset import FieldSightXFormViewSet
from onadata.apps.fsforms.viewsets.ScheduleViewset import ScheduleViewset, DayViewset
from onadata.apps.fsforms.viewsets.AssignedXFormListApiViewSet import AssignedXFormListApi
from onadata.apps.fsforms.viewsets.FSXFormSubmissionApiViewset import FSXFormSubmissionApi
from onadata.apps.fsforms.viewsets.GroupsViewset import GroupViewSet
from onadata.apps.fsforms.viewsets.SiteFormsViewset import SiteFormViewSet
from onadata.apps.fsforms.viewsets.StageViewset import StageViewSet, MainStageViewSet, SiteMainStageViewSet, \
        SubStageViewSet
from onadata.apps.fsforms.viewsets.XformsViewset import XFormViewSet
from .views import (
    LibraryFormsListView,
    FormsListView,
    GroupListView,
    GroupCreateView,
    GroupUpdateView,
    StageListView,
    StageUpdateView,
    StageCreateView,
    add_sub_stage,
    stage_details,
    stage_add_form,
    ScheduleListView,
    ScheduleCreateView,
    # ScheduleUpdateView,
    assign, fill_form_type,
    fill_details_stage,
    fill_details_schedule,
    schedule_add_form,
    AssignedFormsListView,
    html_export, instance,
    show,
    api,
    download_jsonform,
    delete_data,
    data_view,
    site_forms,
    site_stages,
    setup_site_stages,
    stage_add,
    site_survey,
    create_schedule,
    setup_project_stages, project_stage_add, instance_detail, alter_answer_status, project_survey,
    project_create_schedule, project_edit_schedule, edit_main_stage, edit_sub_stage, edit_schedule, responses,
    MyOwnFormsListView, share_level, site_general, edit_general, project_general, project_responses,
    project_html_export, deploy_survey, deploy_stages, deploy_general)

# router = routers.DefaultRouter()
# router.register(r'api/groups', GroupViewSet)
# router.register(r'api/stage', StageViewSet)
# router.register(r'api/main-stages', MainStageViewSet)
# router.register(r'api/schedule', ScheduleViewset)
# router.register(r'api/day', DayViewset)
# router.register(r'api/fsxform', FieldSightXFormViewSet)


urlpatterns = [
        url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        # url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        url(r'^assigned/$', MyOwnFormsListView.as_view(), name='forms-list'),
        # assigned form list to a user(site supervisor)
        url(r'^assigned-form-list/$', AssignedFormsListView.as_view(), name='assigned-form-list'),

        url(r'^group/$', GroupListView.as_view(), name='group-list'),
        url(r'^group/add/$', GroupCreateView.as_view(), name='group-add'),
        url(r'^group/(?P<pk>\d+)/$', GroupUpdateView.as_view(), name='group-edit'),

        url(r'^stage/$', StageListView.as_view(), name='stages-list'),
        url(r'^stage/add/(?P<site_id>\d+)/$', stage_add, name='stage-add'),
        url(r'^responses/(?P<site_id>\d+)/$', responses, name='site-responses'),
        url(r'^project-responses/(?P<project_id>\d+)/$', project_responses, name='project-responses'),
        url(r'^project-stage/add/(?P<id>\d+)/$', project_stage_add, name='project-stage-add'),
        url(r'^stage/(?P<pk>\d+)/$', StageUpdateView.as_view(), name='stage-edit'),
        url(r'^stage-add-sub-stage/(?P<pk>\d+)/$', add_sub_stage, name='stage-add-sub-stage'),
        url(r'^stage-detail/(?P<pk>\d+)/$', stage_details, name='stages-detail'),
        url(r'^stage-add-form/(?P<pk>\d+)/$', stage_add_form, name='stage-add-form'),
        url(r'^stage-edit/(?P<stage>\d+)/(?P<id>\d+)/(?P<is_project>\d)/$', edit_main_stage, name='edit-main-stage'),
        url(r'^sub-stage-edit/(?P<stage>\d+)/(?P<id>\d+)/(?P<is_project>\d)/$', edit_sub_stage, name='edit-sub-stage'),

        # url(r'^schedule/$', ScheduleListView.as_view(), name='schedules-list'),
        url(r'^schedule/add/(?P<site_id>\d+)/$', create_schedule, name='schedule-add'),
        # url(r'^schedule/(?P<pk>\d+)/$', ScheduleUpdateView.as_view(), name='schedule-edit'),
        url(r'^schedule/(?P<id>\d+)/$', edit_schedule, name='schedule-edit'),
        url(r'^general/(?P<id>\d+)/$', edit_general, name='edit-general'),
        url(r'^deploy-stages/(?P<id>\d+)/$', deploy_stages, name='deploy-stages'),
        url(r'^deploy-survey/(?P<id>\d+)/$', deploy_survey, name='deploy-survey'),
        url(r'^deploy-general/(?P<id>\d+)/$', deploy_general, name='deploy-general'),
        url(r'^schedule-add-form/(?P<pk>\d+)/$', schedule_add_form, name='schedule-add-form'),

        url(r'^project/schedule/add/(?P<id>\d+)/$', project_create_schedule, name='project-schedule-add'),
        url(r'^project/schedule/edit/(?P<id>\d+)/$', project_edit_schedule, name='project-schedule-edit'),
        url(r'^site-stage/(?P<site_id>\d+)$', site_stages, name='site-stages'),
        url(r'^setup-site-stage/(?P<site_id>\d+)$', setup_site_stages, name='setup-site-stages'),
        url(r'^setup-project-stage/(?P<id>\d+)$', setup_project_stages, name='setup-project-stages'),
        url(r'^site-survey/(?P<site_id>\d+)$', site_survey, name='site-survey'),
        url(r'^site-general/(?P<site_id>\d+)$', site_general, name='site-general'),
        url(r'^project-general/(?P<project_id>\d+)$', project_general, name='project-general'),
        url(r'^project-survey/(?P<project_id>\d+)$', project_survey, name='project-survey'),

        url(r'^assign/(?P<pk>\d+)/$', assign, name='assign'),
        url(r'^fill-form-type/(?P<pk>\d+)/$', fill_form_type, name='fill_form_type'),
        url(r'^fill-details-stage/(?P<pk>\d+)/$', fill_details_stage, name='fill_details_stage'),
        url(r'^fill-details-schedule/(?P<pk>\d+)/$', fill_details_schedule, name='fill_details_schedule'),
]


urlpatterns = urlpatterns + [
        url(r'^assignedFormList/(?P<site_id>\d+)$', AssignedXFormListApi.as_view({'get': 'list'}), name='form-list'),
        # url(r'^(?P<pk>[\d+^/]+)/form\.xml$',
        #         AssignedXFormListApi.as_view({'get': 'retrieve'}),
        #         name='download_xform'),
        url(r'^(?P<pk>\d+)/form\.xml$',
                'onadata.apps.fsforms.views.download_xform', name='download_xform'),

        url(r'^(?P<pk>\d+)/(?P<site_id>\d+)$', AssignedXFormListApi.as_view({'get': 'manifest'}), name='manifest-url'),

        url(r'^submission/(?P<pk>\d+)/(?P<site_id>\d+)$',
            FSXFormSubmissionApi.as_view({'post': 'create', 'head': 'create'}),
                                                        name='submissions'),
]

urlpatterns = urlpatterns + [
        url(r'reports/(?P<fsxf_id>\d+)$', html_export, name='formpack_html_export'),
        url(r'project-responses/(?P<fsxf_id>\d+)$', project_html_export, name='project_html_export'),
        url(r'^forms/(?P<fsxf_id>\d+)/instance', instance, name='instance'),
        url(r'^forms/(?P<fsxf_id>\d+)/(?P<instance_id>\d+)$', instance_detail, name='instance_detail'),
        url(r'^forms/alter-answer-status/(?P<instance_id>\d+)/(?P<status>\d)/(?P<fsid>\d+)$', alter_answer_status, name='alter-answer-status'),
]

urlpatterns = urlpatterns + [
    # kobo main urls

    url(r'^mongo_view_api/(?P<fsxf_id>\d+)/api$', api, name='mongo_view_api'),
    #  kobo main view
    url(r'^show/(?P<fsxf_id>\d+)$', show, name='show'),
    url(r'^forms/(?P<fsxf_id>\d+)/delete_data$', delete_data, name='delete_data'),
#
]

urlpatterns = urlpatterns + [
            # kobo main urls logger vies

    url(r'^forms/(?P<fsxf_id>\d+)/form\.json',  download_jsonform,  name='download_jsonform'),

]

urlpatterns = urlpatterns + [
            # kobo main urls viewer vies

    url(r'^data-view/(?P<fsxf_id>\d+)$',  data_view,  name='data_view'),

]
urlpatterns = urlpatterns + [
            # urls for api

    url(r'^api/site/(?P<site_id>\d+)$', SiteFormViewSet.as_view({'get': 'list'}), name='form-list'),

]

urlpatterns = urlpatterns + [
            # urls for angular forms

    url(r'^site-forms/(?P<site_id>\d+)$', site_forms, name='site-forms'),
    url(r'^api/xform$', XFormViewSet.as_view({'get': 'list'}), name='xform-list'),

]

urlpatterns = urlpatterns + [

    url(r'^api/site-main-stages/(?P<site_id>\d+)$', SiteMainStageViewSet.as_view({'get': 'list'}), name='main-stage-list'),
    url(r'^api/site-schedules/(?P<site_id>\d+)$', ScheduleViewset.as_view({'get': 'list'}), name='schedule-list'),
    url(r'^api/sub-stages/(?P<main_stage>\d+)$', SubStageViewSet.as_view({'get': 'list'}), name='sub-stage-list'),
    url(r'^share/(?P<id>[\w-]+)/(?P<counter>\d+)$', share_level, name='share'),

]

# urlpatterns += router.urls



