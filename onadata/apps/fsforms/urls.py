from django.conf.urls import url
from onadata.apps.fsforms.viewsets import AssignedXFormListApi, FSXFormSubmissionApi
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
        ScheduleUpdateView,
        assign, fill_form_type,
        fill_details_stage,
        fill_details_schedule,
        schedule_add_form,
        AssignedFormsListView,
        html_export)

# router = MultiLookupRouter(trailing_slash=False)
urlpatterns = [
        url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        url(r'^assigned/$', FormsListView.as_view(), name='forms-list'),
        # assigned form list to a user(site supervisor)
        url(r'^assigned-form-list/$', AssignedFormsListView.as_view(), name='assigned-form-list'),

        url(r'^group/$', GroupListView.as_view(), name='group-list'),
        url(r'^group/add/$', GroupCreateView.as_view(), name='group-add'),
        url(r'^group/(?P<pk>[0-9]+)/$', GroupUpdateView.as_view(), name='group-edit'),

        url(r'^stage/$', StageListView.as_view(), name='stage-list'),
        url(r'^stage/add/$', StageCreateView.as_view(), name='stage-add'),
        url(r'^stage/(?P<pk>[0-9]+)/$', StageUpdateView.as_view(), name='stage-edit'),
        url(r'^stage-add-sub-stage/(?P<pk>[0-9]+)/$', add_sub_stage, name='stage-add-sub-stage'),
        url(r'^stage-detail/(?P<pk>[0-9]+)/$', stage_details, name='stage-detail'),
        url(r'^stage-add-form/(?P<pk>[0-9]+)/$', stage_add_form, name='stage-add-form'),

        url(r'^schedule/$', ScheduleListView.as_view(), name='schedule-list'),
        url(r'^schedule/add/$', ScheduleCreateView.as_view(), name='schedule-add'),
        url(r'^schedule/(?P<pk>[0-9]+)/$', ScheduleUpdateView.as_view(), name='schedule-edit'),
        url(r'^schedule-add-form/(?P<pk>[0-9]+)/$', schedule_add_form, name='schedule-add-form'),

        url(r'^assign/(?P<pk>[0-9]+)/$', assign, name="assign"),
        url(r'^fill-form-type/(?P<pk>[0-9]+)/$', fill_form_type, name="fill_form_type"),
        url(r'^fill-details-stage/(?P<pk>[0-9]+)/$', fill_details_stage, name="fill_details_stage"),
        url(r'^fill-details-schedule/(?P<pk>[0-9]+)/$', fill_details_schedule, name="fill_details_schedule"),
]


urlpatterns = urlpatterns + [
        url(r"^assignedFormList/(?P<site_id>[0-9]+)$",
                AssignedXFormListApi.as_view({'get': 'list'}), name='form-list'),
        # url(r"^(?P<pk>[\d+^/]+)/form\.xml$",
        #         AssignedXFormListApi.as_view({'get': 'retrieve'}),
        #         name="download_xform"),
        url(r"^(?P<pk>[0-9]+)/form\.xml$",
                'onadata.apps.fsforms.views.download_xform', name="download_xform"),

        url(r"^(?P<pk>[0-9]+)/(?P<site_id>[0-9]+)$",
                AssignedXFormListApi.as_view({'get': 'manifest'}),
                name='manifest-url'),

        url(r"^submission/(?P<pk>[0-9]+)/(?P<site_id>[0-9]+]+)$",
                FSXFormSubmissionApi.as_view({'post': 'create', 'head': 'create'}),
                                                        name='submissions'),
]

urlpatterns = urlpatterns + [
        url(r"reports/(?P<fsxf_id>[0-9]+)$",
        html_export, name='formpack_html_export'),

]
