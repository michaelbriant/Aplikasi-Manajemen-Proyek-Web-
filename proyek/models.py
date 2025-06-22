from django.db import models
from django.utils import timezone

class TeamMember(models.Model):
    GENDER_CHOICES = [
        ('L', 'Laki - Laki'),
        ('P', 'Perempuan'),
    ]

    name = models.CharField(max_length=100)
    birth_date = models.DateField("Tanggal Lahir", blank=True, null=True)
    gender = models.CharField("Jenis Kelamin", max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    skills = models.TextField("Deskripsi Kompetensi", blank=True, null=True)
    role = models.TextField("Deskripsi Pengalaman", blank=True, null=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = [
        ('Perencanaan', 'Perencanaan'),
        ('Berlangsung', 'Berlangsung'),
        ('Tertunda', 'Tertunda'),
        ('Berhenti', 'Berhenti'),
        ('siap_dideploy', 'Siap untuk Dideploy'),
        ('Selesai', 'Selesai'),
    ]

    name = models.CharField("Nama Proyek", max_length=200)
    description = models.TextField("Deskripsi Singkat Proyek")
    location = models.CharField("Lokasi", max_length=150)
    start_date = models.DateField("Tanggal Mulai")
    end_date = models.DateField("Tanggal Selesai")
    supervisor = models.CharField("Supervisor", max_length=100)
    status = models.CharField("Status Proyek", max_length=20, choices=STATUS_CHOICES, default='Perencanaan')
    members = models.ManyToManyField('TeamMember', through='ProjectMember', blank=True)
    final_evaluation = models.TextField("Evaluasi Akhir", blank=True, null=True)
    final_report = models.FileField("Laporan Akhir", upload_to='laporan_akhir/', blank=True, null=True)
    supervisor_signed = models.BooleanField("Ditandatangani Supervisor", default=False)
    owner_signed = models.BooleanField("Ditandatangani Pemilik Proyek", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProjectMember(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    role = models.CharField("Peran", max_length=100)

    def __str__(self):
        return f"{self.member.name} - {self.role}"
    
class Pekerjaan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pekerjaan')
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField()
    lokasi = models.CharField(max_length=150)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    pelaksana = models.CharField(max_length=100, blank=True, null=True)
    supervisor = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama

class Aktivitas(models.Model):
    pekerjaan = models.ForeignKey(Pekerjaan, on_delete=models.CASCADE, related_name='aktivitas')
    nama = models.CharField(max_length=255)
    waktu_pelaksanaan = models.DateField()
    pelaksana = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nama

class PenutupanProyek(models.Model):
    proyek = models.OneToOneField(Project, on_delete=models.CASCADE)
    evaluasi = models.TextField()
    tanda_tangan = models.FileField(upload_to='tanda_tangan/')
    tanggal_tutup = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Penutupan {self.proyek.name}"
    
class IntegrasiPesan(models.Model):
    TUJUAN_CHOICES = [
        ('IE', 'Intelligence Engineering'),
        ('IC', 'Intelligence Creation'),
        ('IM', 'Implementation'),
    ]

    proyek = models.ForeignKey(Project, on_delete=models.CASCADE)
    tujuan = models.CharField(max_length=2, choices=TUJUAN_CHOICES)
    dikirim = models.BooleanField(default=False)
    status_terakhir = models.CharField(max_length=100, blank=True, null=True)
    tanggal_dikirim = models.DateTimeField(auto_now_add=True)
    respon = models.TextField(blank=True, null=True)
    isi_pesan = models.TextField(blank=True, null=True)
    asal = models.CharField(
        max_length=10,
        choices=[('system', 'System'), ('external', 'External')],
        default='system'
    )
    waktu = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.get_tujuan_display()} - {self.proyek.name}"