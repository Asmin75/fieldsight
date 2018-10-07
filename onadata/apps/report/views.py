import json
from django.shortcuts import render, get_object_or_404
from onadata.apps.report.report_utils import get_multiple_options_count
from django.views.generic import View, ListView, CreateView, UpdateView
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView
from onadata.apps.fieldsight.rolemixins import ProjectRoleMixin, ReportRoleMixin
from onadata.apps.report.forms import ProjectReportListForm
from onadata.apps.report.models import ReportDashboard
from onadata.apps.fieldsight.models import Project
from django.core.urlresolvers import reverse_lazy, reverse

class GetSelectTypeCount(View):
    def post(self, request, **kwargs):
    	data = json.loads(request.body)
        question_name = data['body'].get('question_name')
        fsxf_id = data['body'].get('fsxf_id')
        response = get_multiple_options_count(self.kwargs.get('pk'), fsxf_id, question_name)
        status = 500 if response.get('status', 'ok') == "failed" else 200
        return JsonResponse(response.get('result', []), safe=False, status=status)


# class ReportDashboardView(View):
#     def get(self, request, **kwargs):
#         question_name = request.POST.get('question_name')
#         response = get_multiple_options_count(pk, fsxf_id, question_name)
#         status = 200 if response.get('status', 'ok') == "failed" else 500
#         return JsonResponse(json.loads(response.get('result', {})), status=status)

#     def post(self, request, **kwargs):
#         question_name = request.POST.get('question_name')
#         response = get_multiple_options_count(pk, fsxf_id, question_name)
#         status = 200 if response.get('status', 'ok') == "failed" else 500
#         return JsonResponse(json.loads(response.get('result', {})), status=status)


class DeleteProjectReport(ReportRoleMixin, View):
    def get(self, request, **kwargs):
    	report = get_object_or_404(ReportDashboard, pk=self.kwargs.get('pk'))
    	report.is_active = False
    	report.save()
    	return HttpResponseRedirect(reverse('report:all', kwargs={'pk': report.project_id }))


class DeployProjectReport(ReportRoleMixin, View):
    def get(self, request, **kwargs):
    	report = get_object_or_404(ReportDashboard, pk=self.kwargs.get('pk'))
    	report.is_deployed = True
    	report.save()
    	return HttpResponseRedirect(reverse('report:all', kwargs={'pk': report.project_id }))


class UnDeployProjectReport(ReportRoleMixin, View):
    def get(self, request, **kwargs):
        report = get_object_or_404(ReportDashboard, pk=self.kwargs.get('pk'))
        report.is_deployed = False
        report.save()
        return HttpResponseRedirect(reverse('report:all', kwargs={'pk': report.project_id }))


class ProjectReportList(ProjectRoleMixin, ListView):
    model = ReportDashboard
    template_name = 'report/report_list.html'
    paginate_by = 9
    
    def get_context_data(self, **kwargs):
	    context = super(ProjectReportList, self).get_context_data(**kwargs)
	    context['project'] = self.project
	    return context

    def get_queryset(self):
        self.project = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        query = self.request.GET.get("q", None)
        return ReportDashboard.objects.filter(project=self.project) if not query else ReportDashboard.objects.filter(name__icontains=query, project=self.project)

class ReportCreate(ProjectRoleMixin, CreateView):
    
    form_class = ProjectReportListForm
    model = ProjectReportList
    template_name = 'report/report_form.html'

    def get_context_data(self, **kwargs):
        context = super(ReportCreate, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context

    def form_valid(self, form):
        form.instance.project_id = self.kwargs.get('pk')
        return super(ReportCreate, self).form_valid(form)
        
    def get_success_url(self):
        return reverse('report:all', kwargs={'pk': self.object.project_id })


class ReportUpdate(ReportRoleMixin, UpdateView):
    form_class = ProjectReportListForm
    model = ProjectReportList

    def get_success_url(self):
        return reverse('report:all', kwargs={'pk': self.object.project_id})
