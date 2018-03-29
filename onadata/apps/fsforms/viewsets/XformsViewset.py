from django.db.models import Q
from rest_framework import viewsets

from onadata.apps.fsforms.serializers.XformSerializer import XFormListSerializer
from onadata.apps.logger.models import XForm


class XFormViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing xforms.
    """
    queryset = XForm.objects.filter(deleted_xform=None)
    serializer_class = XFormListSerializer

    def get_queryset(self):
        if self.request.user.user_roles.filter(group__name="Super Admin").exists():
            return self.queryset.filter(deleted_xform=None)
        return self.queryset.filter(Q(user=self.request.user) |
                Q(user__user_profile__organization=self.request.organization), deleted_xform=None)
