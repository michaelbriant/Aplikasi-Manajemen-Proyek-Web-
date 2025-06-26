# Mengimpor modul forms dari Django
from django import forms

# Mengimpor model yang digunakan dalam form
from .models import Project, TeamMember, Pekerjaan, Aktivitas

# Mengimpor form autentikasi bawaan Django
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User


# =========================== #
# Form untuk membuat / edit proyek
# =========================== #
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['members']  # Field 'members' tidak ditampilkan di form
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),  # Input kalender untuk tanggal mulai
            'end_date': forms.DateInput(attrs={'type': 'date'}),    # Input kalender untuk tanggal selesai
            'status': forms.Select(),  # Dropdown untuk memilih status (opsional)
        }


# =========================== #
# Form khusus untuk menutup proyek (evaluasi akhir)
# =========================== #
class TutupProyekForm(forms.ModelForm):
    # Tambahan field boolean untuk tanda tangan supervisor dan pemilik proyek
    supervisor_signed = forms.BooleanField(label="Ditandatangani Supervisor", required=True)
    owner_signed = forms.BooleanField(label="Ditandatangani Pemilik Proyek", required=True)

    class Meta:
        model = Project
        fields = ['final_evaluation', 'final_report', 'supervisor_signed', 'owner_signed']
        widgets = {
            'final_evaluation': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tuliskan evaluasi akhir proyek di sini...'
            }),
            'final_report': forms.ClearableFileInput(attrs={
                'accept': '.pdf,.doc,.docx'
            }),  # Upload laporan akhir
        }


# =========================== #
# Form untuk menambahkan anggota tim
# =========================== #
class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'  # Menampilkan semua field dari model
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  # Input tanggal lahir
            'photo': forms.ClearableFileInput(attrs={
                'class': 'hidden-input',
                'id': 'fileUpload'
            })  # Upload foto
        }


# =========================== #
# Form untuk menambahkan / mengedit pekerjaan dalam proyek
# =========================== #
class PekerjaanForm(forms.ModelForm):
    class Meta:
        model = Pekerjaan
        # UBAH DARI 'exclude' MENJADI 'fields' DAN TAMBAHKAN 'status'
        fields = [
            'nama', 'deskripsi', 'lokasi', 'tanggal_mulai',
            'tanggal_selesai', 'pelaksana', 'supervisor', 'status' # <-- Tambahkan 'status' di sini
        ]
        widgets = {
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(), # <-- Tambahkan widget ini untuk dropdown
        }


# =========================== #
# Form untuk menambahkan / mengedit aktivitas dalam pekerjaan
# =========================== #
class AktivitasForm(forms.ModelForm):
    class Meta:
        model = Aktivitas
        # UBAH DARI 'exclude' MENJADI 'fields' DAN TAMBAHKAN 'status'
        fields = [
            'nama', 'waktu_pelaksanaan', 'pelaksana', 'status' # <-- Tambahkan 'status' di sini
        ]
        widgets = {
            'waktu_pelaksanaan': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(), # <-- Tambahkan widget ini untuk dropdown
        }


# =========================== #
# Form untuk pendaftaran akun pengguna baru (registrasi)
# =========================== #
class CustomUserCreationForm(UserCreationForm):
    # Menambahkan input email ke dalam form
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
        # Kostumisasi tampilan field
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


# =========================== #
# Form untuk mengganti password (tanpa login)
# =========================== #
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'Masukkan Kata Sandi Baru'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Konfirmasi Kata Sandi Baru'
        })