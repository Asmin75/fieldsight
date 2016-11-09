from datetime import datetime
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from onadata.apps.fieldsight.models import Site, Project, Organization


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_roles")
    group = models.ForeignKey(Group)
    started_at = models.DateTimeField(default=datetime.now)
    ended_at = models.DateTimeField(blank=True, null=True)
    site = models.ForeignKey(Site, null=True, blank=True, related_name='site_roles')
    project = models.ForeignKey(Project, null=True, blank=True, related_name='project_roles')
    organization = models.ForeignKey(Organization, null=True, blank=True, related_name='organization_roles')

    def __unicode__(self):
        return 'user: {}\'s role : {}'.format(self.user.__unicode__(), self.group.__unicode__())

    def as_json(self):
        return dict(
            user = self.user.get_full_name(), email = self.user.email
            )

    class Meta:
        unique_together = ('user', 'group', 'organization', 'project','site')

    def clean(self):
        if self.group.name == 'Site Supervisor' and not self.site_id:
            raise ValidationError({
                'site': ValidationError(_('Missing site.'), code='required'),
            })
        if self.group.name == 'Central Engineer' and not self.site_id:
            raise ValidationError({
                'site': ValidationError(_('Missing site.'), code='required'),
            })

        if self.group.name == 'Project Manager' and not self.project_id:
            raise ValidationError({
                'project': ValidationError(_('Missing Project.'), code='required'),
            })

        if self.group.name == 'Organization Admin' and not self.organization_id:
            raise ValidationError({
                'organization': ValidationError(_('Missing Organization.'), code='required'),
            })

    def save(self, *args, **kwargs):
        if self.group.name == 'Super Admin':
            self.organization = None
            self.project = None
            self.site = None
        elif self.group.name == 'Organization Admin':
            self.project = None
            self.site = None
        elif self.group.name == 'Project Manager':
            self.site = None
            self.organization = self.project.organization

        elif self.group.name == 'Site Supervisor':
            self.project = self.site.project
            self.organization = self.site.project.organization

        elif self.group.name == 'Central Engineer':
            self.project = self.site.project
            self.organization = self.site.project.organization
        super(UserRole, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        if self.group.name == 'Super Admin':
            self.organization = None
            self.project = None
            self.site = None
        elif self.group.name == 'Organization Admin':
            self.project = None
            self.site = None
        elif self.group.name == 'Project Manager':
            self.site = None
            self.organization = self.project.organization

        elif self.group.name == 'Site Supervisor':
            self.project = self.site.project
            self.organization = self.site.project.organization

        elif self.group.name == 'Central Engineer':
            self.project = self.site.project
            self.organization = self.site.project.organization
        super(UserRole, self).update(*args, **kwargs)

    @staticmethod
    def is_active(user,group):
        return UserRole.objects.filter(user=user, group=group,ended_date=None).count()

    @staticmethod
    def get_active_roles(user):
        return UserRole.objects.filter(user=user,ended_at=None).select_related('group', 'organization')

    @staticmethod
    def get_active_site_roles(user):
        return UserRole.objects.filter(user=user, ended_at=None, group__name="Site Supervisor").\
            select_related('group', 'site')\

    @staticmethod
    def project_managers(project):
        return UserRole.objects.filter(project=project, ended_at=None, group__name="Project Manager").\
            select_related('group', 'project')

    @staticmethod
    def organization_admins(organization):
        return UserRole.objects.filter(organization=organization, ended_at=None, group__name="Organization Admin").\
            select_related('group', 'organization')\

    @staticmethod
    def central_engineers(site):
        return UserRole.objects.filter(site=site, ended_at=None, group__name="Central Engineer").\
            select_related('group', 'site')
