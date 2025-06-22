from django import forms
from .models import Project, TeamMember, Pekerjaan, Aktivitas
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['members']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(),  # optional
        }

class TutupProyekForm(forms.ModelForm):
    supervisor_signed = forms.BooleanField(label="Ditandatangani Supervisor", required=True)
    owner_signed = forms.BooleanField(label="Ditandatangani Pemilik Proyek", required=True)

    class Meta:
        model = Project
        fields = ['final_evaluation', 'final_report', 'supervisor_signed', 'owner_signed']
        widgets = {
            'final_evaluation': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tuliskan evaluasi akhir proyek di sini...'}),
            'final_report': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'hidden-input', 'id': 'fileUpload'}),
        }

from .models import Project, TeamMember, Pekerjaan, Aktivitas

class PekerjaanForm(forms.ModelForm):
    class Meta:
        model = Pekerjaan
        exclude = ['project']
        widgets = {
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date'}),
        }

class AktivitasForm(forms.ModelForm):
    class Meta:
        model = Aktivitas
        exclude = ['pekerjaan']
        widgets = {
            'waktu_pelaksanaan': forms.DateInput(attrs={'type': 'date'}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Email',
        'required': True,
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Nama Pengguna',
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Kata Sandi',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Konfirmasi Kata Sandi',
            'class': 'form-control'
        })

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'Masukkan Kata Sandi Baru'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Konfirmasi Kata Sandi Baru'
        })
