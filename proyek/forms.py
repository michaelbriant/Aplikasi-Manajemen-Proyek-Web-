from django import forms
from .models import Project, TeamMember
from .models import AktivitasPekerjaan


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['members']  # ⬅️ Ini kuncinya!
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AktivitasPekerjaanForm(forms.ModelForm):
    class Meta:
        model = AktivitasPekerjaan
        fields = '__all__'
        widgets = {
            'time': forms.DateInput(attrs={'type': 'date'}),
        }
