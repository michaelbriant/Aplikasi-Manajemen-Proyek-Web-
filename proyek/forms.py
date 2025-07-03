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
    """
    Form untuk membuat atau mengedit data proyek.
    Berdasarkan model `Project`.
    """
    class Meta:
        """
        Meta class untuk konfigurasi form ProjectForm.
        """
        model = Project
        # 'members' dikecualikan karena akan ditangani secara terpisah (misalnya melalui JavaScript atau field kustom).
        exclude = ['members']
        widgets = {
            # Menggunakan input HTML5 type 'date' untuk field tanggal
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            # Menggunakan dropdown (select) untuk field status, akan mengambil opsi dari model
            'status': forms.Select(),
        }


# =========================== #
# Form khusus untuk menutup proyek (evaluasi akhir)
# =========================== #
class TutupProyekForm(forms.ModelForm):
    """
    Form khusus untuk proses penutupan proyek.
    Menyertakan field tambahan untuk konfirmasi tanda tangan supervisor dan pemilik proyek,
    serta field untuk evaluasi akhir dan laporan akhir.
    """
    # Field boolean untuk menandakan apakah supervisor sudah menandatangani
    supervisor_signed = forms.BooleanField(label="Ditandatangani Supervisor", required=True)
    # Field boolean untuk menandakan apakah pemilik proyek sudah menandatangani
    owner_signed = forms.BooleanField(label="Ditandatangani Pemilik Proyek", required=True)

    class Meta:
        """
        Meta class untuk konfigurasi form TutupProyekForm.
        """
        model = Project
        # Hanya field-field ini yang akan muncul di form penutupan proyek
        fields = ['final_evaluation', 'final_report', 'supervisor_signed', 'owner_signed']
        widgets = {
            'final_evaluation': forms.Textarea(attrs={
                'rows': 4, # Menentukan jumlah baris textarea
                'placeholder': 'Tuliskan evaluasi akhir proyek di sini...' # Placeholder teks
            }),
            # Widget untuk input file yang bisa dikosongkan (clearable)
            'final_report': forms.ClearableFileInput(attrs={
                'accept': '.pdf,.doc,.docx' # Membatasi jenis file yang bisa diunggah
            }),
        }


# =========================== #
# Form untuk menambahkan anggota tim
# =========================== #
class TeamMemberForm(forms.ModelForm):
    """
    Form untuk menambah atau mengedit data anggota tim.
    Berdasarkan model `TeamMember`.
    """
    class Meta:
        """
        Meta class untuk konfigurasi form TeamMemberForm.
        """
        model = TeamMember
        # '__all__' berarti semua field dari model TeamMember akan disertakan dalam form
        fields = '__all__'
        widgets = {
            # Menggunakan input HTML5 type 'date' untuk tanggal lahir
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            # Widget untuk input file foto dengan CSS class khusus ('hidden-input')
            # dan ID ('fileUpload') untuk kustomisasi tampilan melalui JavaScript/CSS.
            'photo': forms.ClearableFileInput(attrs={
                'class': 'hidden-input',
                'id': 'fileUpload'
            })
        }


# =========================== #
# Form untuk menambahkan / mengedit pekerjaan dalam proyek
# =========================== #
class PekerjaanForm(forms.ModelForm):
    """
    Form untuk menambah atau mengedit pekerjaan yang terkait dengan sebuah proyek.
    Berdasarkan model `Pekerjaan`.
    """
    class Meta:
        """
        Meta class untuk konfigurasi form PekerjaanForm.
        """
        model = Pekerjaan
        # Menentukan field-field yang akan ditampilkan di form
        fields = [
            'nama', 'deskripsi', 'lokasi', 'tanggal_mulai',
            'tanggal_selesai', 'pelaksana', 'supervisor', 'status' # Field 'status' ditambahkan
        ]
        widgets = {
            # Menggunakan input HTML5 type 'date' untuk tanggal mulai dan selesai
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date'}),
            # Menggunakan dropdown (select) untuk field status
            'status': forms.Select(),
        }


# =========================== #
# Form untuk menambahkan / mengedit aktivitas dalam pekerjaan
# =========================== #
class AktivitasForm(forms.ModelForm):
    """
    Form untuk menambah atau mengedit aktivitas yang terkait dengan sebuah pekerjaan.
    Berdasarkan model `Aktivitas`.
    """
    class Meta:
        """
        Meta class untuk konfigurasi form AktivitasForm.
        """
        model = Aktivitas
        # Menentukan field-field yang akan ditampilkan di form
        fields = [
            'nama', 'waktu_pelaksanaan', 'pelaksana', 'status' # Field 'status' ditambahkan
        ]
        widgets = {
            # Menggunakan input HTML5 type 'date' untuk waktu pelaksanaan
            'waktu_pelaksanaan': forms.DateInput(attrs={'type': 'date'}),
            # Menggunakan dropdown (select) untuk field status
            'status': forms.Select(),
        }


# =========================== #
# Form untuk pendaftaran akun pengguna baru (registrasi)
# =========================== #
class CustomUserCreationForm(UserCreationForm):
    """
    Form kustom untuk pendaftaran pengguna baru.
    Mewarisi dari `UserCreationForm` bawaan Django dan menambahkan field `email`.
    Melakukan kustomisasi widget untuk tampilan input.
    """
    # Menambahkan field email ke form registrasi.
    # `required=True` berarti email wajib diisi.
    # Menggunakan `EmailInput` dan menambahkan atribut HTML untuk placeholder dan class CSS.
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Email',
        'required': True,
        'class': 'form-control'
    }))

    class Meta:
        """
        Meta class untuk konfigurasi form CustomUserCreationForm.
        """
        model = User
        # Menentukan field-field dari model User yang akan digunakan
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        """
        Metode inisialisasi kustom untuk CustomUserCreationForm.
        Digunakan untuk menambahkan atribut HTML seperti placeholder dan class CSS
        ke field-field form.
        """
        super().__init__(*args, **kwargs)
        # Mengupdate atribut widget untuk field username
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Nama Pengguna',
            'class': 'form-control'
        })
        # Mengupdate atribut widget untuk field password1 (kata sandi baru)
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Kata Sandi',
            'class': 'form-control'
        })
        # Mengupdate atribut widget untuk field password2 (konfirmasi kata sandi)
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Konfirmasi Kata Sandi',
            'class': 'form-control'
        })


# =========================== #
# Form untuk mengganti password (tanpa login)
# =========================== #
class CustomSetPasswordForm(SetPasswordForm):
    """
    Form kustom untuk mengatur ulang kata sandi pengguna tanpa memerlukan kata sandi lama.
    Mewarisi dari `SetPasswordForm` bawaan Django.
    Melakukan kustomisasi widget untuk placeholder.
    """
    def __init__(self, *args, **kwargs):
        """
        Metode inisialisasi kustom untuk CustomSetPasswordForm.
        Digunakan untuk menambahkan atribut HTML seperti placeholder
        ke field-field form.
        """
        super().__init__(*args, **kwargs)
        # Mengupdate atribut widget untuk field new_password1
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'Masukkan Kata Sandi Baru'
        })
        # Mengupdate atribut widget untuk field new_password2
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Konfirmasi Kata Sandi Baru'
        })