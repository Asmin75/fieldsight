from django import forms
from onadata.apps.report.models import ProjectReportList

class ProjectReportListForm(forms.ModelForm):
    class Meta:
        model = ProjectReportList
        fields = ('name',)