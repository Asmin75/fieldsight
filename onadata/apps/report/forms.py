from django import forms
from onadata.apps.report.models import ReportDashboard

class ProjectReportListForm(forms.ModelForm):
    class Meta:
        model = ReportDashboard
        fields = ('name',)