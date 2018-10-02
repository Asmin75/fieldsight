from django.conf.urls import url
from .views import ( GetSelectTypeCount, ReportCreate, ProjectReportList, DeleteProjectReport, ReportUpdate )

urlpatterns = [
    
    url(r'^api/getSelectQuestionCount/(?P<pk>\d+)/$', GetSelectTypeCount.as_view(), name='GetSelectTypeCount'),




    url(r'^all/(?P<pk>\d+)/$', ProjectReportList.as_view(), name='all'),
    url(r'^create/(?P<pk>\d+)/$', ReportCreate.as_view(), name='create'),
    url(r'^update/(?P<pk>\d+)/$', ReportUpdate.as_view(), name='update'),
    url(r'^deploy/(?P<pk>\d+)/$', DeployProjectReport.as_view(), name='deploy'),
    url(r'^delete/(?P<pk>\d+)/$', DeleteProjectReport.as_view(), name='delete'),

    ]

