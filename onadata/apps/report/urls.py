from django.conf.urls import url
from .views import ( GetSelectTypeCount, ReportCreate, ProjectReportList, DeleteProjectReport, DeployProjectReport, UnDeployProjectReport, ReportUpdate )
from .viewsets.report import ReportDashboardViewSet
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    
    url(r'^api/getSelectQuestionCount/(?P<pk>\d+)/$', csrf_exempt(GetSelectTypeCount.as_view()), name='GetSelectTypeCount'),
    url(r'^api/dashboard-data/(?P<pk>\d+)/$', ReportDashboardViewSet.as_view({'get': 'retrieve', 'post': 'update'}), name='dashboardData'),




    url(r'^all/(?P<pk>\d+)/$', ProjectReportList.as_view(), name='all'),
    url(r'^create/(?P<pk>\d+)/$', ReportCreate.as_view(), name='create'),
    url(r'^update/(?P<pk>\d+)/$', ReportUpdate.as_view(), name='update'),
    url(r'^deploy/(?P<pk>\d+)/$', DeployProjectReport.as_view(), name='deploy'),
    url(r'^undeploy/(?P<pk>\d+)/$', UnDeployProjectReport.as_view(), name='undeploy'),
    url(r'^delete/(?P<pk>\d+)/$', DeleteProjectReport.as_view(), name='delete'),

    ]

