from django.shortcuts import render, get_object_or_404
from onadata.apps.report.report_utils import get_multiple_options_count
from django.views.generic import View
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView
from onadata.apps.fieldsight.rolemixins import ProjectRoleMixin, ReportRoleMixin
from onadata.apps.report.forms import ProjectReportListForm

class GetSelectTypeCount(View):
    def get(self, request, **kwargs):
    	question_name = request.POST.get('question_name')
        response = get_multiple_options_count(pk, fsxf_id, question_name)
        status = 200 if response.get('status', 'ok') == "failed" else 500
        return JsonResponse(json.loads(response.get('result', {})), status=status)


class DeleteProjectReport(ReportRoleMixin, View):
    def get(self, request, **kwargs):
    	report = get_object_or_404(ReportDashboard, name=self.kwargs['pk'])
    	report.is_active = False
    	report.save()
    	return HttpResponseRedirect(reverse('report:all', kwargs={'pk': report.project_id }))


class DeployProjectReport(ReportRoleMixin, View):
    def get(self, request, **kwargs):
    	report = get_object_or_404(ReportDashboard, name=self.kwargs['pk'])
    	report.is_deployed = True
    	report.save()
    	return HttpResponseRedirect(reverse('report:all', kwargs={'pk': report.project_id }))


class ProjectReportList(ProjectRoleMixin, ListView):
	model = Site
    template_name = 'report/report_list.html'
    paginate_by = 9
    
    def get_context_data(self, **kwargs):
	    context = super(ProjectReportList, self).get_context_data(**kwargs)
	    context['project'] = self.project
	    return context

    def get_queryset(self):
        self.project = get_object_or_404(Project, name=self.kwargs['pk'])
        query = self.request.GET.get("q", None)
        return ReportDashboard.objects.filter(project=self.project) if not query else ReportDashboard.objects.filter(name__icontains=query, project=self.project)

class ReportCreate(ProjectRoleMixin, CreateView):
    
    form_class = ProjectReportListForm
    model = ProjectReportList

    def get_context_data(self, **kwargs):
        context = super(ProjectCreateView, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context

    def form_valid(self, form):
        self.object = form.save(project_id=self.kwargs.get('pk'), new=True)
        return HttpResponseRedirect(reverse('report:all', kwargs={'pk': report.project_id }))


class ReportUpdate(ReportRoleMixin, UpdateView):
    form_class = ProjectReportListForm
    model = ProjectReportList

    def get_success_url(self):
        return reverse('report:all', kwargs={'pk': self.object.project_id})