from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from onadata.apps.staff.models import Team, StaffProject, Bank, Staff, Attendance
from onadata.apps.userrole.models import UserRole

class ProjectForm(forms.ModelForm):
    class Meta:
        model = StaffProject
        fields = ('name',)

class TeamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        self.fields['leader'].choices = [(role.user.id, role.user.user_profile.getname()) for role in UserRole.objects.filter(project_id__in=[137,183, 105,129, 119], ended_at=None).distinct('user_id').order_by('user_id', 'user__first_name')]
    
    class Meta:
        model = Team
        fields = ('leader','name')


class StaffForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        self.fields['bank'].empty_label = "Other"
    
    class Meta:
        model = Staff
        fields = ('first_name','last_name', 'gender', 'ethnicity','address','phone_number','bank','bank_name', 'account_number', 'photo', 'designation',)

class StaffEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)
        self.fields['bank'].empty_label = "Other"

        current_team = self.instance.team
        self.fields['team'].choices = [(team.id, team.name) for team in current_team.staffproject.team_project.all()]
    
    class Meta:
        model = Staff
        fields = ('first_name','team','last_name', 'gender', 'ethnicity','address','phone_number','bank','bank_name', 'account_number', 'photo', 'designation',)

class AttendanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.fields['staffs'].choices = [(staff.id, staff) for staff in Staff.objects.filter(team_id=kwargs.get('instance').team_id, is_deleted=False)]
        self.fields['staffs'].required = False

    staffs = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
    class Meta:
        model = Attendance
        fields = ('staffs',)
