from django.conf.urls import url
from .views import ( GetSelectTypeCount )

urlpatterns = [
    
    url(r'^api/report/getSelectQuestionCount/(?P<pk>\d+)/$', GetSelectTypeCount.as_view(), name='GetSelectTypeCount'),

    ]

