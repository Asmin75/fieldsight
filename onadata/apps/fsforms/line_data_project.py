import datetime
from collections import OrderedDict

from django.db.models import Count

from .models import FInstance

def date_range(start, end, intv):
    start = datetime.datetime.strptime(start,"%Y%m%d")
    end = datetime.datetime.strptime(end,"%Y%m%d")
    diff = (end  - start ) / intv
    for i in range(intv):
        yield (start + diff * i)
    yield end


class LineChartGenerator(object):

    def __init__(self, project):
        self.project = project
        self.date_list = list(date_range(project.date_created.strftime("%Y%m%d"), datetime.datetime.today().strftime("%Y%m%d"), 6))

    def get_count(self, date):
        date = date + datetime.timedelta(days=1)
        return self.project.project_instances.filter(date__lte=date.date()).count()

    def data(self):
        d = OrderedDict()
        dt = self.date_list
        for date in dt:
            count = self.get_count(date)
            d[date.strftime('%Y-%m-%d')] = count
        return d


class LineChartGeneratorOrganization(object):

    def __init__(self, organization):
        self.organization = organization
        self.date_list = list(date_range(organization.date_created.strftime("%Y%m%d"), datetime.datetime.today().strftime("%Y%m%d"), 6))

    def get_count(self, date):
        date = date + datetime.timedelta(days=1)
        return FInstance.objects.filter(project__organization=self.organization, date__lte=date.date()).count()

    def data(self):
        d = OrderedDict()
        dt = self.date_list
        for date in dt:
            count = self.get_count(date)
            d[date.strftime('%Y-%m-%d')] = count
        return d


class LineChartGeneratorSite(object):

    def __init__(self, site):
        self.site = site
        self.date_list = list(date_range(site.date_created.strftime("%Y%m%d"), datetime.datetime.today().strftime("%Y%m%d"), 6))

    def get_count(self, date):
        date = date + datetime.timedelta(days=1)
        return self.site.site_instances.filter(date__lte=date.date()).count()

    def data(self):
        d = OrderedDict()
        dt = self.date_list
        for date in dt:
            count = self.get_count(date)
            d[date.strftime('%Y-%m-%d')] = count
        return d


class ProgressGeneratorSite(object):

    def __init__(self, site):
        self.site = site

    def data(self):
        d = OrderedDict()
        main_stages = self.site.stages.filter(stage__isnull=True)
        for ms in main_stages:
            sub_stages = ms.parent.filter(stage_forms__isnull=False)
            for sub_stage in sub_stages:
                fsform = sub_stage.stage_forms
                approved_submission = fsform.site_form_instances.filter(form_status=3)
                try:
                    date = approved_submission[0].date
                    d[date.strftime('%Y-%m-%d')] = ms.order +sub_stage.order*0.1
                except:
                    pass
        return d


