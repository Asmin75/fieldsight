from django.contrib import admin
from .models import UserInvite, Organization, Project, Site, Region, SiteType

admin.site.register(UserInvite)
admin.site.register(Organization)
admin.site.register(Project)
admin.site.register(Site)
admin.site.register(Region)
admin.site.register(SiteType)