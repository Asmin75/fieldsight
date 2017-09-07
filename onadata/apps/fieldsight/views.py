import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.response import TemplateResponse
from django.views.generic import ListView, TemplateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.forms.forms import NON_FIELD_ERRORS


import django_excel as excel
from registration.backends.default.views import RegistrationView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from channels import Group as ChannelGroup

from onadata.apps.eventlog.models import FieldSightLog
from onadata.apps.fieldsight.bar_data_project import BarGenerator
from onadata.apps.fsforms.Submission import Submission
from onadata.apps.fsforms.line_data_project import LineChartGenerator, LineChartGeneratorOrganization, \
    LineChartGeneratorSite
from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile
from .mixins import (LoginRequiredMixin, SuperAdminMixin, OrganizationMixin, ProjectMixin, SiteView,
                     CreateView, UpdateView, DeleteView, OrganizationView as OView, ProjectView as PView,
                     group_required, OrganizationViewFromProfile, ReviewerMixin, MyOwnOrganizationMixin,
                     MyOwnProjectMixin, ProjectMixin)
from .rolemixins import SiteSupervisorRoleMixin, ProjectRoleView, ReviewerRoleMixin, ProjectRoleMixin, OrganizationRoleMixin, ReviewerRoleMixinDeleteView, ProjectRoleMixinDeleteView
from .models import Organization, Project, Site, ExtraUserDetail, BluePrints, UserInvite
from .forms import (OrganizationForm, ProjectForm, SiteForm, RegistrationForm, SetProjectManagerForm, SetSupervisorForm,
                    SetProjectRoleForm, AssignOrgAdmin, UploadFileForm, BluePrintForm, ProjectFormKo)
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from django.core.files.storage import FileSystemStorage

@login_required
def dashboard(request):
    current_role = request.roles
    if current_role.count() == 1:
        if current_role[0].group.name == "Site Supervisor":
            return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': current_role[0].site.pk}))
        if current_role[0].group.name == "Reviewer":
            return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': current_role[0].site.pk}))
        if current_role[0].group.name == "Project Manager":
            return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': current_role[0].project.pk}))
        if current_role[0].group.name == "Organization Admin":
            return HttpResponseRedirect(reverse("fieldsight:organizations-dashboard",
                                                kwargs={'pk': current_role[0].organization.pk}))
    if current_role.count() > 1:
        return HttpResponseRedirect(reverse("fieldsight:roles-dashboard"))

    total_users = User.objects.all().count()
    total_organizations = Organization.objects.all().count()
    total_projects = Project.objects.all().count()
    total_sites = Site.objects.all().count()
    data = serialize('custom_geojson', Site.objects.filter(is_survey=False, is_active=True), geometry_field='location',
                        fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone','id'))
    fs_forms = FieldSightXF.objects.all()
    fs_forms = list(fs_forms)
    outstanding = flagged = approved = rejected = 0
    for form in fs_forms:
        if form.form_status == 0:
            outstanding += 1
        elif form.form_status == 1:
            flagged +=1
        elif form.form_status == 2:
            approved +=1
        else:
            rejected +=1

    dashboard_data = {
        'total_users': total_users,
        'total_organizations': total_organizations,
        'total_projects': total_projects,
        'total_sites': total_sites,
        'outstanding': outstanding,
        'flagged': flagged,
        'approved': approved,
        'rejected': rejected,
        'data': data,
    }
    return TemplateResponse(request, "fieldsight/fieldsight_dashboard.html", dashboard_data)


def get_site_images(site_id):
    query = {'fs_site': str(site_id), '_deleted_at': {'$exists': False}}
    return settings.MONGO_DB.instances.find(query).sort([("_id", 1)]).limit(20)


def site_images(request, pk):
    cursor = get_site_images(pk)
    cursor = list(cursor)
    medias = []
    for index, doc in enumerate(cursor):
        for media in cursor[index].get('_attachments', []):
            if media:
                medias.append(media.get('download_url', ''))

    return JsonResponse({'images':medias[:5]})

class Organization_dashboard(LoginRequiredMixin, OrganizationRoleMixin, TemplateView):
    template_name = "fieldsight/organization_dashboard.html"
    def get_context_data(self, **kwargs):
        dashboard_data = super(Organization_dashboard, self).get_context_data(**kwargs)
        obj = Organization.objects.get(pk=self.kwargs.get('pk'))
        peoples_involved = obj.organization_roles.filter(group__name = "Organization Admin").order_by('user__first_name')
        sites = Site.objects.filter(project__organization=obj,is_survey=False, is_active=True)
        data = serialize('custom_geojson', sites, geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))
        projects = Project.objects.filter(organization=obj)
        total_projects = len(projects)
        total_sites = len(sites)
        outstanding, flagged, approved, rejected = obj.get_submissions_count()
        total_users = UserProfile.objects.filter(organization=obj).count()

        bar_graph = BarGenerator(sites)

        line_chart = LineChartGeneratorOrganization(obj)
        line_chart_data = line_chart.data()

        dashboard_data = {
            'obj': obj,
            'projects': projects,
            'sites': sites,
            'peoples_involved': peoples_involved,
            'total_users': total_users,
            'total_projects': total_projects,
            'total_sites': total_sites,
            'outstanding': outstanding,
            'flagged': flagged,
            'approved': approved,
            'rejected': rejected,
            'data': data,
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
            'progress_data': bar_graph.data.values(),
            'progress_labels': bar_graph.data.keys(),
        }
        return dashboard_data

class Project_dashboard(ProjectRoleMixin, TemplateView):
    template_name = "fieldsight/project_dashboard.html"
    
    def get_context_data(self, **kwargs):
        dashboard_data = super(Project_dashboard, self).get_context_data(**kwargs)
        obj = Project.objects.get(pk=self.kwargs.get('pk'))

        peoples_involved = obj.project_roles.filter(group__name__in=["Project Manager", "Reviewer"]).distinct('user')

        sites = obj.sites.filter(is_active=True, is_survey=False)
        data = serialize('custom_geojson', sites, geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone','id',))

        total_sites = len(sites)
        total_survey_sites = obj.sites.filter(is_survey=True).count()
        outstanding, flagged, approved, rejected = obj.get_submissions_count()
        bar_graph = BarGenerator(sites)

        line_chart = LineChartGenerator(obj)
        line_chart_data = line_chart.data()
        dashboard_data = {
            'obj': obj,
            'peoples_involved': peoples_involved,
            'total_sites': total_sites,
            'total_survey_sites': total_survey_sites,
            'outstanding': outstanding,
            'flagged': flagged,
            'approved': approved,
            'rejected': rejected,
            'data': data,
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
            'progress_data': bar_graph.data.values(),
            'progress_labels': bar_graph.data.keys(),
    }
        return dashboard_data


class SiteSurveyListView(LoginRequiredMixin, ProjectMixin, TemplateView):
    def get(self, request, pk):
        return TemplateResponse(request, "fieldsight/site_survey_list.html", {'project':pk})


class SiteDashboardView(ReviewerRoleMixin, TemplateView):
    template_name = 'fieldsight/site_dashboard.html'

    def get_context_data(self, **kwargs):
        dashboard_data = super(SiteDashboardView, self).get_context_data(**kwargs)
        obj = Site.objects.get(pk=self.kwargs.get('pk'))
        peoples_involved = obj.site_roles.all().order_by('user__first_name')
        data = serialize('custom_geojson', [obj], geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))

        line_chart = LineChartGeneratorSite(obj)
        line_chart_data = line_chart.data()

        outstanding, flagged, approved, rejected = obj.get_site_submission()
        dashboard_data = {
            'obj': obj,
            'peoples_involved': peoples_involved,
            'outstanding': outstanding,
            'flagged': flagged,
            'approved': approved,
            'rejected': rejected,
            'data': data,
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
        }
        return dashboard_data

class SiteSupervisorDashboardView(SiteSupervisorRoleMixin, TemplateView):
    template_name = 'fieldsight/site_supervisor_dashboard.html'

    def get_context_data(self, **kwargs):
        dashboard_data = super(SiteSupervisorDashboardView, self).get_context_data(**kwargs)
        obj = Site.objects.get(pk=self.kwargs.get('pk'))
        peoples_involved = obj.site_roles.all().order_by('user__first_name')
        data = serialize('custom_geojson', [obj], geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))

        line_chart = LineChartGeneratorSite(obj)
        line_chart_data = line_chart.data()

        outstanding, flagged, approved, rejected = obj.get_site_submission()
        dashboard_data = {
            'obj': obj,
            'peoples_involved': peoples_involved,
            'outstanding': outstanding,
            'flagged': flagged,
            'approved': approved,
            'rejected': rejected,
            'data': data,
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
        }
        return dashboard_data

class OrganizationView(object):
    model = Organization
    success_url = reverse_lazy('fieldsight:organizations-list')
    form_class = OrganizationForm


class UserDetailView(object):
    model = User
    success_url = reverse_lazy('users:users')
    form_class = RegistrationForm


class OrganizationListView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, ListView):
    pass


class OrganizationCreateView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, CreateView):
    def form_valid(self, form):
        self.object = form.save()
        noti = self.object.logs.create(source=self.request.user, type=9, title="new Organization",
                                       organization=self.object, content_object=self.object,
                                       description="{} created a new organization named {1}".
                                       format(self.request.user.get_full_name(), self.object.name))
        result = {}
        result['description'] = '{} created a new organization named {1} '.format(noti.source.get_full_name(), self.object.name)
        result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.id)).send({"text": json.dumps(result)})
        ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())


class OrganizationUpdateView(OrganizationView, OrganizationRoleMixin, UpdateView):
    def get_success_url(self):
        return reverse('fieldsight:organizations-dashboard', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = form.save()
        noti = self.object.logs.create(source=self.request.user, type=13, title="edit Organization",
                                       organization=self.object, content_object=self.object,
                                       description="{} changed the details of organization named {1}".
                                       format(self.request.user.get_full_name(), self.object.name))
        result = {}
        result['description'] = noti.description
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.id)).send({"text": json.dumps(result)})
        ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())



class OrganizationDeleteView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, DeleteView):
    pass

@login_required
@group_required('admin')
def alter_org_status(request, pk):
    try:
        obj = Organization.objects.get(pk=int(pk))
            # alter status method on custom user
        if obj.is_active:
            obj.is_active = False
            messages.info(request, 'Organization {0} Deactivated.'.format(obj.name))
        else:
            obj.is_active = True
            messages.info(request, 'Organization {0} Activated.'.format(obj.name))
        obj.save()
    except:
        messages.info(request, 'Organization {0} not found.'.format(obj.name))
    return HttpResponseRedirect(reverse('fieldsight:organizations-list'))

#
# @login_required
# @group_required('admin')
# def add_org_admin_old(request, pk):
#     obj = get_object_or_404(
#         Organization, id=pk)
#     if request.method == 'POST':
#         form = SetOrgAdminForm(request.POST)
#         user = int(form.data.get('user'))
#         group = Group.objects.get(name__exact="Organization Admin")
#         role = UserRole(user_id=user, group=group, organization=obj)
#         role.save()
#         messages.add_message(request, messages.INFO, 'Organization Admin Added')
#         return HttpResponseRedirect(reverse('fieldsight:organizations-list'))
#     else:
#         form = SetOrgAdminForm(instance=obj)
#     return render(request, "fieldsight/add_admin.html", {'obj':obj,'form':form})

class OrganizationadminCreateView(LoginRequiredMixin, OrganizationRoleMixin, TemplateView):

    def get(self, request, pk=None):
        organization = get_object_or_404(Organization, id=pk)
        form = AssignOrgAdmin(request=request)
        scenario = 'Assign'
        return render(request, 'fieldsight/add_admin_form.html',
                      {'form': form, 'scenario': scenario, 'obj': organization})

    def post(self, request):
        organization = get_object_or_404(Organization, id=id)
        group = Group.objects.get(name__exact="Organization Admin")
        role_obj = UserRole(organization=organization, group=group)
        form = AssignOrgAdmin(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
            messages.add_message(request, messages.INFO, 'Organization Admin Added')
            return HttpResponseRedirect(reverse("fieldsight:organizations-dashboard", kwargs={'pk': id}))


@login_required
@group_required('Organization')
def alter_proj_status(request, pk):
    try:
        obj = Project.objects.get(pk=int(pk))
            # alter status method on custom user
        if obj.is_active:
            obj.is_active = False
            messages.info(request, 'Project {0} Deactivated.'.format(obj.name))
        else:
            obj.is_active = True
            messages.info(request, 'Project {0} Activated.'.format(obj.name))
        obj.save()
    except:
        messages.info(request, 'Project {0} not found.'.format(obj.name))
    return HttpResponseRedirect(reverse('fieldsight:projects-list'))


@login_required
@group_required('Project')
def add_proj_manager(request, pk):
    obj = get_object_or_404(
        Project, pk=pk)
    group = Group.objects.get(name__exact="Project Manager")
    role_obj = UserRole(project=obj, group=group)
    scenario = 'Assign'
    if request.method == 'POST':
        form = SetProjectManagerForm(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
        messages.add_message(request, messages.INFO, 'Project Manager Added')
        return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': obj.pk}))
    else:
        form = SetProjectManagerForm(instance=role_obj, request=request)
    return render(request, "fieldsight/add_project_manager.html", {'obj':obj,'form':form, 'scenario':scenario})


@login_required
@group_required('Project')
def alter_site_status(request, pk):
    try:
        obj = Site.objects.get(pk=int(pk))
        if obj.is_active:
            obj.is_active = False
            messages.info(request, 'Site {0} Deactivated.'.format(obj.name))
        else:
            obj.is_active = True
            messages.info(request, 'Site {0} Activated.'.format(obj.name))
        obj.save()
    except:
        messages.info(request, 'Site {0} not found.'.format(obj.name))
    return HttpResponseRedirect(reverse('fieldsight:sites-list'))


@login_required
@group_required('Reviewer')
def add_supervisor(request, pk):
    obj = get_object_or_404(
        Site, pk=int(pk))
    group = Group.objects.get(name__exact="Site Supervisor")
    role_obj = UserRole(site=obj, group=group)
    if request.method == 'POST':
        form = SetSupervisorForm(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
        messages.add_message(request, messages.INFO, 'Site Supervisor Added')
        return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': obj.pk}))
    else:
        form = SetSupervisorForm(instance=role_obj, request=request)
    return render(request, "fieldsight/add_supervisor.html", {'obj':obj,'form':form})


@login_required
@group_required('Project')
def add_central_engineer(request, pk):
    obj = get_object_or_404(
        Project, pk=pk)
    group = Group.objects.get(name__exact="Reivewer")
    role_obj = UserRole(project=obj, group=group)
    scenario = 'Assign'
    if request.method == 'POST':
        form = SetProjectRoleForm(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
        messages.add_message(request, messages.INFO, 'Reviewer Added')
        return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': obj.pk}))
    else:
        form = SetProjectRoleForm(instance=role_obj, request=request,)
    return render(request, "fieldsight/add_central_engineer.html", {'obj':obj,'form':form, 'scenario':scenario})


@login_required
@group_required('Project')
def add_project_role(request, pk):
    obj = get_object_or_404(
        Project, pk=pk)
    role_obj = UserRole(project=obj)
    scenario = 'Assign People'
    form = SetProjectRoleForm(instance=role_obj, request=request)
    if request.method == 'POST':
        form = SetProjectRoleForm(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
            messages.add_message(request, messages.INFO, '{} Added'.format(role_obj.group.name))
            return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': obj.pk}))
    existing_staffs = obj.get_staffs
    return render(request, "fieldsight/add_central_engineer.html", {'obj':obj,'form':form, 'scenario':scenario,
                                                                    "existing_staffs":existing_staffs})


class ProjectView(object):
    model = Project
    success_url = reverse_lazy('fieldsight:project-list')
    form_class = ProjectForm

class ProjectRoleView(object):
    model = Project
    success_url = reverse_lazy('fieldsight:project-list')
    form_class = ProjectForm

class ProjectListView(ProjectRoleView, OrganizationMixin, ListView):
    pass


class ProjectCreateView(ProjectView, OrganizationRoleMixin, CreateView):

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.organization_id = self.kwargs.get('pk')
        self.object.save()
        noti = self.object.logs.create(source=self.request.user, type=10, title="new Project",
                                       organization=self.object.organization, content_object=self.object,
                                       description='{0} created new project named {1}'.format(
                                           self.request.user.get_full_name(), self.object.name))
        result = {}
        result['description'] = noti.description
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})


        return HttpResponseRedirect(self.object.get_absolute_url())


class ProjectUpdateView(ProjectView, ProjectRoleMixin, UpdateView):
    def get_success_url(self):
        return reverse('fieldsight:project-dashboard', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = form.save()
        noti = self.object.logs.create(source=self.request.user, type=14, title="Edit Project",
                                       organization=self.object.organization,
                                       project=self.object, content_object=self.object,
                                       description='{0} changed the details of project named {1}'.format(
                                           self.request.user.get_full_name(), self.object.name))
        result = {}
        result['description'] = noti.description
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.organization.id)).send({"text": json.dumps(result)})
        ChannelGroup("project-{}".format(self.object.id)).send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())



class ProjectDeleteView(ProjectView, ProjectRoleMixinDeleteView, DeleteView):
    def delete(self,*args, **kwargs):
        self.object = self.get_object()
        # noti = self.object.logs.create(source=self.request.user, type=4, title="new Site",
        #                                organization=self.object.organization,
        #                                description="new project {0} deleted by {1}".
        #                                format(self.object.name, self.request.user.username))
        # result = {}
        # result['description'] = 'new project {0} deleted by {1}'.format(self.object.name, self.request.user.username)
        # result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})
        return HttpResponseRedirect(self.get_success_url())



class SiteView(PView):
    model = Site
    success_url = reverse_lazy('fieldsight:sites-list')
    form_class = SiteForm


class SiteListView(SiteView, ReviewerRoleMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(SiteListView, self).get_context_data(**kwargs)
        context['form'] = SiteForm()
        return context


class SiteCreateView(SiteView, ProjectRoleMixin, CreateView):

    def get_success_url(self):
        return reverse('fieldsight:site-dashboard', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        self.object = form.save()
        noti = self.object.logs.create(source=self.request.user, type=11, title="new Site",
                                       organization=self.object.project.organization,
                                       project=self.object.project, content_object=self.object, extra_object=self.object.project,
                                       description='{0} created a new site named {1} in {2}'.format(self.request.user.get_full_name(),
                                                                                 object.name, object.project.name))
        result = {}
        result['description'] = '{0} created a new site named {1} in {2}'.format(self.request.user.get_full_name(),
                                                                                 object.name, object.project.name)
        result['url'] = noti.get_absolute_url()
        ChannelGroup("project-{}".format(self.object.project.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())



class SiteUpdateView(SiteView, ReviewerMixin, UpdateView):
    def get_success_url(self):
        return reverse('fieldsight:site-dashboard', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = form.save()
        noti = self.object.logs.create(source=self.request.user, type=15, title="edit Site",
                                       organization=self.object.project.organization, project=self.object.project, content_object=self.object,
                                       description='{0} changed the details of site named {1}'.format(
                                           self.request.user.get_full_name(), self.object.name))
        result = {}
        result['description'] = 'new site {0} updated by {1}'.format(self.object.name, self.request.user.username)
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
        ChannelGroup("project-{}".format(self.object.project.id)).send({"text": json.dumps(result)})
        ChannelGroup("site-{}".format(self.object.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())


class SiteDeleteView(SiteView, ProjectRoleMixin, DeleteView):
    def delete(self,*args, **kwargs):
        self.object = self.get_object()
        # noti = self.object.logs.create(source=self.request.user, type=3, title="new Site",
        #                                organization=self.object.project.organization,
        #                                description="new site {0} deleted by {1}".
        #                                format(self.object.name, self.request.user.username))
        # result = {}
        # result['description'] = 'new site {0} deleted by {1}'.format(self.object.name, self.request.user.username)
        # result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())


@group_required("Project")
@api_view(['POST'])
def ajax_upload_sites(request, pk):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        count = 0
        project = Project(pk=pk)
        try:
            sites = request.FILES['file'].get_records()
            count = len(sites)
            with transaction.atomic():
                for site in sites:
                    site = dict((k,v) for k,v in site.iteritems() if v is not '')
                    lat = site.get("longitude", 85.3240)
                    long = site.get("latitude", 27.7172)
                    location = Point(lat, long, srid=4326)
                    type_id = int(site.get("type", "1"))
                    _site, created = Site.objects.get_or_create(identifier=str(site.get("id")), name=site.get("name"),
                                                                project=project, type_id=type_id)
                    _site.phone = site.get("phone")
                    _site.address = site.get("address")
                    _site.public_desc = site.get("public_desc"),
                    _site.additional_desc = site.get("additional_desc")
                    _site.location=location
                    _site.save()
            if count:
                noti = project.logs.create(source=request.user, type=12, title="Bulk Sites",
                                       organization=project.organization,
                                       project=project, content_object=project,
                                       extra_message=count + "Sites",
                                       description='{0} created a {1} sites in {2}'.
                                           format(request.user.get_full_name(), count, project.name))
                result = {}
                result['description'] = noti.description
                result['url'] = noti.get_absolute_url()
                ChannelGroup("project-{}".format(project.id)).send({"text": json.dumps(result)})
            return Response({'msg': 'ok'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'file':e.message}, status=status.HTTP_400_BAD_REQUEST)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@group_required("Project")
@api_view(['POST'])
def ajax_save_site(request, pk):
    form = SiteForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Site Data'}, status=status.HTTP_400_BAD_REQUEST)


@group_required("Organization")
@api_view(['POST'])
def ajax_save_project(request):
    form = ProjectFormKo(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Project Data'}, status=status.HTTP_400_BAD_REQUEST)

class UploadSitesView(ProjectMixin, TemplateView):

    def get(self, request, pk):
        form = UploadFileForm()
        return render(request, 'fieldsight/upload_sites.html',{'form':form, 'project':pk})

    def post(self, request, pk=id):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            project = Project(pk=pk)
            try:
                sites = request.FILES['file'].get_records()
                with transaction.atomic():
                    for site in sites:
                        site = dict((k, v) for k, v in site.iteritems() if v is not '')
                        lat = site.get("longitude", 85.3240)
                        long = site.get("latitude", 27.7172)
                        location = Point(lat, long, srid=4326)
                        type_id = int(site.get("type", "1"))
                        _site, created = Site.objects.get_or_create(identifier=str(site.get("id")),
                                                                    name=site.get("name"),
                                                                    project=project, type__id=type_id)
                        _site.phone = site.get("phone")
                        _site.address = site.get("address")
                        _site.public_desc = site.get("public_desc"),
                        _site.additional_desc = site.get("additional_desc")
                        _site.location = location
                        _site.save()
                messages.info(request, 'Site Upload Succesfull')
                return HttpResponseRedirect(reverse('fieldsight:site-list'))
            except Exception as e:
                form.full_clean()
                form._errors[NON_FIELD_ERRORS] = form.error_class(['Sites Upload Failed, UnSupported Data'])
                messages.warning(request, 'Site Upload Failed, UnSupported Data ')
        return render(request, 'fieldsight/upload_sites.html', {'form': form, 'project': pk})


def download(request):
    sheet = excel.pe.Sheet([[1, 2],[3, 4]])
    return excel.make_response(sheet, "csv")


class UserListView(ProjectMixin, OrganizationViewFromProfile, ListView):
    def get_template_names(self):
        return ['fieldsight/user_list.html']

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        return context


class FilterUserView(TemplateView):
    def get(self, *args, **kwargs):
        return redirect('fieldsight:user-list')

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        role = request.POST.get('role')
        groups = Group.objects.all()
        object_list = User.objects.filter(is_active=True, pk__gt=0)
        if name:
            object_list = object_list.filter(
                Q(first_name__contains=name) | Q(last_name__contains=name) | Q(username__contains=name))
        if role and role != '0':
            object_list = object_list.filter(user_roles__group__id=role)
        if hasattr(request, "organization") and request.organization:
            object_list = object_list.filter(user_roles__organization=request.organization)
        return render(request, 'fieldsight/user_list.html', {'object_list': object_list, 'groups': groups})



class CreateUserView(LoginRequiredMixin, SuperAdminMixin, UserDetailView, RegistrationView):
    def register(self, request, form, *args, **kwargs):
        with transaction.atomic():
            new_user = super(CreateUserView, self).register(
                request, form, *args, **kwargs)
            is_active = form.cleaned_data['is_active']
            new_user.first_name = request.POST.get('name', '')
            new_user.is_active = is_active
            new_user.is_superuser = True
            new_user.save()
            organization = int(form.cleaned_data['organization'])
            org = Organization.objects.get(pk=organization)
            profile = UserProfile(user=new_user, organization=org)
            profile.save()
            # noti = profile.logs.create(source=self.request.user, type=0, title="new User",
            #                         organization=profile.organization, description="new user {0} created by {1}".
            #                         format(new_user.username, self.request.user.username))
            # result = {}
            # result['description'] = 'new user {0} created by {1}'.format(new_user.username, self.request.user.username)
            # result['url'] = noti.get_absolute_url()
            # ChannelGroup("notify-{}".format(profile.organization.id)).send({"text":json.dumps(result)})
            # ChannelGroup("notify-0").send({"text":json.dumps(result)})

        return new_user

class BluePrintsView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        ImageFormSet = modelformset_factory(BluePrints, form=BluePrintForm, extra=5)
        formset = ImageFormSet(queryset=BluePrints.objects.none())
        return render(request, 'fieldsight/blueprints_form.html', {'formset': formset,'id': self.kwargs.get('id')},)

    def post(self, request, id):
        ImageFormSet = modelformset_factory(BluePrints, form=BluePrintForm, extra=5)
        formset = ImageFormSet(request.POST, request.FILES,
                                   queryset=BluePrints.objects.none())

        if formset.is_valid():
            for form in formset.cleaned_data:
                if 'image' in form:
                    image = form['image']
                    photo = BluePrints(site_id=id, image=image)
                    photo.save()
            messages.success(request,
                             "Blueprints saved!")
            return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': id}))

        formset = ImageFormSet(queryset=BluePrints.objects.none())
        return render(request, 'fieldsight/blueprints_form.html', {'formset': formset, 'id': self.kwargs.get('id')}, )


class ManagePeopleSiteView(LoginRequiredMixin, ReviewerMixin, TemplateView):
    def get(self, request, pk):
        project = Site.objects.get(pk=pk).project
        return render(request, 'fieldsight/manage_people_site.html', {'pk':pk, 'level': "0", 'category':"site", 'organization': project.organization.id, 'project':project.id, 'site':pk})


class ManagePeopleProjectView(LoginRequiredMixin, ProjectMixin, TemplateView):
    def get(self, request, pk):
        organization = Project.objects.get(pk=pk).organization.id
        return render(request, "fieldsight/manage_people_site.html",
                      {'pk': pk, 'level': "1", 'category':"Project Manager", 'organization': organization, 'project': pk})


class ManagePeopleOrganizationView(LoginRequiredMixin, OrganizationMixin, TemplateView):
    def get(self, request, pk):
        return render(request, 'fieldsight/manage_people_site.html', {'pk': pk, 'level': "2", 'category':"Organization Admin", 'organization': pk})


def all_notification(user,  message):
    ChannelGroup("%s" % user).send({
        "text": json.dumps({
            "msg": message
        })
    })

class RolesView(LoginRequiredMixin, TemplateView):
    template_name = "fieldsight/roles_dashboard.html"
    def get_context_data(self, **kwargs):
        context = super(RolesView, self).get_context_data(**kwargs)
        context['org_admin'] = self.request.roles.filter(group__name="Organization Admin")
        context['proj_manager'] = self.request.roles.filter(group__name = "Project Manager")
        context['site_reviewer'] = self.request.roles.filter(group__name = "Reviewer")
        context['site_supervisor'] = self.request.roles.filter(group__name = "Site Supervisor")
        return context


class OrgProjectList(OrganizationRoleMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(OrgProjectList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context
    def get_queryset(self):
        queryset = Project.objects.filter(organization_id=self.kwargs.get('pk'))
        return queryset


class OrgSiteList(OrganizationRoleMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(OrgSiteList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context
    def get_queryset(self):
        queryset = Site.objects.filter(project__organization_id=self.kwargs.get('pk'),is_survey=False, is_active=True)
        return queryset

class ProjSiteList(ProjectRoleMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(ProjSiteList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context
    def get_queryset(self):
        queryset = Site.objects.filter(project_id=self.kwargs.get('pk'),is_survey=False, is_active=True)
        return queryset

class OrgUserList(OrganizationRoleMixin, ListView):
    template_name = "fieldsight/user_list_updated.html"
    def get_context_data(self, **kwargs):
        context = super(OrgUserList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context
    def get_queryset(self):
        #queryset = UserRole.objects.select_related('User').filter(organization_id=self.kwargs.get('pk')).distinct('user_id')
        #queryset = User.objects.select_related('user_profile').filter(user_profile__organization_id=self.kwargs.get('pk'))
        
        queryset = UserRole.objects.select_related('user').filter(organization_id=self.kwargs.get('pk')).distinct('user_id')
        return queryset

class ProjUserList(ProjectRoleMixin, ListView):
    template_name = "fieldsight/user_list_updated.html"
    def get_context_data(self, **kwargs):
        context = super(ProjUserList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context
    def get_queryset(self):
        queryset = UserRole.objects.select_related('user').filter(project_id=self.kwargs.get('pk')).distinct('user_id')
        return queryset

class SiteUserList(ProjectRoleMixin, ListView):
    template_name = "fieldsight/user_list_updated.html"
    def get_context_data(self, **kwargs):
        context = super(SiteUserList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context
    def get_queryset(self):
        queryset = UserRole.objects.select_related('user').filter(site_id=self.kwargs.get('pk')).distinct('user_id')
    
        return queryset

@login_required()
def ajaxgetuser(request):
    user = User.objects.filter(email=request.POST.get('email'))
    html = render_to_string('fieldsight/ajax_temp/ajax_user.html', {'department': User.objects.filter(email=user)})
    return HttpResponse(html)

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

@login_required()
def senduserinvite(request):
    user = User.objects.filter(email=request.POST.get('email'))
    group = Group.objects.get(name=request.POST.get('group'))

    organization_id = None
    project_id =None
    site_id =None

    if RepresentsInt(request.POST.get('organization_id')):
        organization_id = request.POST.get('organization_id')
    if RepresentsInt(request.POST.get('project_id')):
        project_id = request.POST.get('project_id')
    if RepresentsInt(request.POST.get('site_id')):
        site_id = request.POST.get('site_id')


    userinvite = UserInvite.objects.filter(email=request.POST.get('email'), organization_id=organization_id, group=group, project_id=project_id,  site_id=site_id, is_used=False)

    if userinvite:
        return HttpResponse('<script> alert("Invite already sent."); <script>')

    if user:
        userrole = UserRole.objects.filter(user=user[0], group=group, organization_id=organization_id, project_id=project_id, site_id=site_id).order_by('-id')
        
        if userrole:
            if userrole[0].ended_at==None:
                return HttpResponse('Already has the role.') 
        
        invite = UserInvite(email=request.POST.get('email'), by_user_id=request.user.id ,group=group, token=get_random_string(length=32), organization_id=organization_id, project_id=project_id, site_id=site_id)

        invite.save()
        organization = Organization.objects.get(pk=1)
        # noti = invite.logs.create(source=user[0], type=9, title="new Role",
        #                                organization_id=request.POST.get('organization_id'),
        #                                description="{0} sent you an invite to join {1} as the {2}.".
        #                                format(request.user.username, organization.name, invite.group.name,))
        # result = {}
        # result['description'] = 'new site {0} deleted by {1}'.format(self.object.name, self.request.user.username)
        # result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})

    else:
        invite = UserInvite(email=request.POST.get('email'), by_user_id=request.user.id, token=get_random_string(length=32), group=group, project_id=project_id, organization_id=organization_id,  site_id=site_id)
        invite.save()
    current_site = get_current_site(request)
    subject = 'Invitation for Role'
    message = render_to_string('fieldsight/email_sample.html',
    {
        'email': invite.email,
        'domain': current_site.domain,
        'invite_id': urlsafe_base64_encode(force_bytes(invite.pk)),
        'token': invite.token,
        'invite': invite,
        })
    email_to = (invite.email,)
    send_mail(subject, message, 'Field Sight', email_to,fail_silently=False)
    return HttpResponse("<script> alert('Sucessfully invited for "+ group.name +" role.');</script>")

# def activate_role(request, invite_idb64, token):
#     try:
#         invite_id = force_text(urlsafe_base64_decode(invite_idb64))
#         invite = UserInvite.objects.filter(id=invite_id, token=token, is_used=False)
#     except (TypeError, ValueError, OverflowError, UserInvite.DoesNotExist):
#         invite = None
#     if invite:
#         user = User.objects.filter(email=invite[0].email)
#         if user:
#             userrole = UserRole(user=user[0], group=invite[0].group, organization=invite[0].organization, project=invite[0].project, site=invite[0].site)
#             userrole.save()
#             return HttpResponse("Sucess")
#         else:

#     return HttpResponse("Failed")
   
class ActivateRole(TemplateView):
    def dispatch(self, request, invite_idb64, token):
        invite_id = force_text(urlsafe_base64_decode(invite_idb64))
        invite = UserInvite.objects.filter(id=invite_id, token=token, is_used=False)
        if invite:
            return super(ActivateRole, self).dispatch(request, invite[0], invite_idb64, token)
        return HttpResponseRedirect(reverse('login'))

    def get(self, request, invite, invite_idb64, token):
        user = User.objects.filter(email=invite.email)
        if invite.is_used==True:
            return render(request, 'fieldsight/invite_action.html',{'invite':invite, 'is_used': True, })
        if user:
            return render(request, 'fieldsight/invite_action.html',{'invite':invite, 'is_used': False,})
        else:
            return render(request, 'fieldsight/invited_user_reg.html',{'invite':invite, 'is_used': False,})
        

    def post(self, request, invite, *args, **kwargs):
        user = User.objects.filter(email=invite.email)
        if user:
            if request.POST.get('response') == "accept":
                userrole = UserRole(user=user[0], group=invite.group, organization=invite.organization, project=invite.project, site=invite.site)
                userrole.save()
            else:
                invite.is_declined = True
            invite.is_used = True
            invite.save()
        else:
            user = User(username=request.POST.get('username'), email=invite.email, first_name=request.POST.get('firstname'), last_name=request.POST.get('lastname'))
            user.set_password(request.POST.get('password1'))
            user.save()
            userrole = UserRole(user=user, group=invite.group, organization=invite.organization, project=invite.project, site=invite.site)
            userrole.save()
            invite.is_used = True
            invite.save()

        if invite.group.name == "Organization Admin":
            noti_type = 1
            content = invite.organization
        elif invite.group.name == "Project Manager":
            noti_type = 2
            content = invite.project
        elif invite.group.name == "Reviewer":
            noti_type = 3
            content = invite.site
        elif invite.group.name == "Site Supervisor":
            noti_type = 4
            content = invite.site
        
        noti = invite.logs.create(source=user, type=noti_type, title="new Role",
                                       organization=invite.organization, project=invite.project, site=invite.site, content_object=content, extra_object=invite.user,
                                       description="{0} was added as the {1} of {2} by {3}.".
                                       format(user.username, invite.group.name, content.name, invite.user ))
        # result = {}
        # result['description'] = 'new site {0} deleted by {1}'.format(self.object.name, self.request.user.username)
        # result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})
        return HttpResponseRedirect(reverse('login'))
            
@login_required()
def checkemailforinvite(request):
    user = User.objects.select_related('user_profile').filter(email__icontains=request.POST.get('email'))
    if user:
        return render(request, 'fieldsight/invite_response.html', {'users': user,})
    else:
        return HttpResponse("No existing User found.<a href='#' onclick='sendnewuserinvite()'>send</a>")


class SummaryReport(TemplateView):
    def get(self, request, pk):
        site = Site.objects.select_related('project').get(pk=pk)
        organization = site.project.organization
        project_managers = site.project.project_roles.filter(group__name="Project_manager").order_by('user__first_name')
        site_reviewers = site.site_roles.filter(group__name="Reviewer").order_by('user__first_name')
        site_supervisors = site.site_roles.filter(group__name="Site Supervisor").order_by('user__first_name')
        data = serialize('custom_geojson', [site], geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))

        line_chart = LineChartGeneratorSite(site)
        line_chart_data = line_chart.data()

        outstanding, flagged, approved, rejected = site.get_site_submission()
        dashboard_data = {
            'site': site,
            'obj':site,
            'project': site.project,
            'organization':organization,
            'outstanding': outstanding,
            'flagged': flagged,
            'approved': approved,
            'rejected': rejected,
            'data': data,
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
        }
        return render(request, 'fieldsight/site_individual_submission_report.html', dashboard_data)
