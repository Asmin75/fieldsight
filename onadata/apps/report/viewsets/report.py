from __future__ import unicode_literals
import datetime
import json
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, BasePermission

from onadata.apps.report.models import ReportDashboard
from onadata.apps.report.serializers.report import ReportSerializer
from rest_framework.authentication import BasicAuthentication
from onadata.apps.api.viewsets.xform_viewset import CsrfExemptSessionAuthentication
from django.shortcuts import render, get_object_or_404

SAFE_METHODS = ('GET', 'POST')

class AccessPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False
        
        if request.group:
            if request.group.name == "Super Admin":
                return True
 
        reportDashboard = get_object_or_404(ReportDashboard, pk=view.kwargs.get('pk'))
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, project_id = reportDashboard.project_id, group_id=2)
        
        if user_role:
            return True

        organization_id = reportDashboard.project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
        
        if user_role_asorgadmin:
            return True

        return False

class ReportDashboardViewSet(viewsets.ModelViewSet):
    queryset = ReportDashboard.objects.all()
    serializer_class = ReportSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (AccessPermission, )

    def filter_queryset(self, queryset):
        return queryset.filter(pk=self.kwargs.get('pk'))