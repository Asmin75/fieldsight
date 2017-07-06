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

    def get_count(self, date):
        return self.project.project_instances.filter(date__contains=date.date()).count()

    def data(self):
        d = OrderedDict()
        dt = [(datetime.datetime.today() - datetime.timedelta(days=x)) for x in range(0,30)]
        dt = dt[::-1]
        for date in dt:
            count = self.get_count(date)
            d[date.date().strftime('%Y-%m-%d')] = count
        return d


class LineChartGeneratorOrganization(object):

    def __init__(self, organization):
        self.organization = organization
        self.date_list = list(date_range(organization.date_created.strftime("%Y%m%d"), datetime.datetime.today().strftime("%Y%m%d"), 6))

    def get_count(self, date):
        return FInstance.objects.filter(project__organization=self.organization, date__lt=date.date()).count()

    def data(self):
        d = OrderedDict()
        dt = self.date_list
        for date in dt:
            count = self.get_count(date)
            # import ipdb
            # ipdb.set_trace()
            d[date.strftime('%Y-%m-%d')] = count
        return d


class LineChartGeneratorSite(object):

    def __init__(self, site):
        self.site = site

    def get_count(self, date):
        return self.site.site_instances.filter(date__contains=date.date()).count()

    def data(self):
        d = OrderedDict()
        dt = [(datetime.datetime.today() - datetime.timedelta(days=x)) for x in range(0,30)]
        dt = dt[::-1]
        for date in dt:
            count = self.get_count(date)
            d[date.date().strftime('%Y-%m-%d')] = count
        return d


