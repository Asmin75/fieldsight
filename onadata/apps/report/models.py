from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from jsonfield import JSONField
from onadata.apps.fieldsight.models import Project


class ReportDashboardAllManager(models.Manager):
    def get_queryset(self):
        return super(ReportDashboardAllManager, self).get_queryset().all()

class ReportDashboardManager(models.Manager):
    def get_queryset(self):
        return super(ReportDashboardManager, self).get_queryset().filter(is_active=True)

class ReportDeployedDashboardManager(models.Manager):
    def get_queryset(self):
        return super(ReportDeployedDashboardManager, self).get_queryset().filter(is_deployed=True, is_active=True)

class ReportDashboard(models.Model):
    project = models.ForeignKey(Project, related_name="project_report_dashboards")
    dashboadData = JSONField(default=dict)
    name = models.CharField(max_length=255, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_updated = models.DateTimeField(null=True, blank=True)
    
    is_deployed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    all_objects = ReportDashboardAllManager()
    objects = ReportDashboardManager()
    deployed_objects = ReportDeployedDashboardManager()
    
    logs = GenericRelation('eventlog.FieldSightLog')
