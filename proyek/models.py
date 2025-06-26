from django.db import models
from django.utils import timezone

# ===== Model Anggota Tim: untuk menyimpan informasi setiap anggota tim proyek =====
class TeamMember(models.Model):
    GENDER_CHOICES = [  # Pilihan untuk jenis kelamin
        ('L', 'Laki - Laki'),
        ('P', 'Perempuan'),
    ]

    name = models.CharField(max_length=100)  # Nama lengkap anggota
    birth_date = models.DateField("Tanggal Lahir", blank=True, null=True)  # Tanggal lahir (opsional)
    gender = models.CharField("Jenis Kelamin", max_length=1, choices=GENDER_CHOICES, blank=True, null=True)  # Jenis kelamin (opsional)
    skills = models.TextField("Deskripsi Kompetensi", blank=True, null=True)  # Daftar skill atau kompetensi
    role = models.TextField("Deskripsi Pengalaman", blank=True, null=True)  # Deskripsi pengalaman atau peran
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)  # Foto profil (opsional)
    created_at = models.DateTimeField(auto_now_add=True)  # Tanggal data dibuat
    updated_at = models.DateTimeField(auto_now=True)  # Tanggal data terakhir diperbarui

    def __str__(self):
        return self.name


# ===== Model Proyek: untuk menyimpan informasi proyek secara keseluruhan =====
class Project(models.Model):
    STATUS_CHOICES = [  # Pilihan status proyek
        ('Perencanaan', 'Perencanaan'),
        ('Berlangsung', 'Berlangsung'),
        ('Tertunda', 'Tertunda'),
        ('Berhenti', 'Berhenti'),
        ('siap_dideploy', 'Siap untuk Dideploy'),
        ('Selesai', 'Selesai'),
    ]

    name = models.CharField("Nama Proyek", max_length=200)  # Nama proyek
    description = models.TextField("Deskripsi Singkat Proyek")  # Ringkasan tentang proyek
    location = models.CharField("Lokasi", max_length=150)  # Lokasi pelaksanaan proyek
    start_date = models.DateField("Tanggal Mulai")  # Tanggal mulai proyek
    end_date = models.DateField("Tanggal Selesai")  # Tanggal akhir proyek
    supervisor = models.CharField("Supervisor", max_length=100)  # Nama supervisor proyek
    status = models.CharField("Status Proyek", max_length=20, choices=STATUS_CHOICES, default='Perencanaan')  # Status saat ini
    members = models.ManyToManyField('TeamMember', through='ProjectMember', blank=True)  # Relasi dengan anggota tim
    final_evaluation = models.TextField("Evaluasi Akhir", blank=True, null=True)  # Evaluasi akhir proyek
    final_report = models.FileField("Laporan Akhir", upload_to='laporan_akhir/', blank=True, null=True)  # File laporan akhir proyek
    supervisor_signed = models.BooleanField("Ditandatangani Supervisor", default=False)  # Tanda tangan supervisor
    owner_signed = models.BooleanField("Ditandatangani Pemilik Proyek", default=False)  # Tanda tangan pemilik proyek
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu pembuatan
    updated_at = models.DateTimeField(auto_now=True)  # Waktu terakhir diperbarui

    def __str__(self):
        return self.name


# ===== Model Perantara ProjectMember: untuk menghubungkan Project dan TeamMember dengan peran khusus =====
class ProjectMember(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)  # Proyek terkait
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)  # Anggota tim terkait
    role = models.CharField("Peran", max_length=100)  # Peran anggota dalam proyek (misal: developer, analis, dst.)

    def __str__(self):
        return f"{self.member.name} - {self.role}"


# ===== Model Pekerjaan: untuk menyimpan daftar pekerjaan dalam suatu proyek =====
class Pekerjaan(models.Model):
    PEKERJAAN_STATUS_CHOICES = [ # Pilihan status pekerjaan
        ('Perencanaan', 'Perencanaan'),
        ('Berlangsung', 'Berlangsung'),
        ('Tertunda', 'Tertunda'),
        ('Berhenti', 'Berhenti'),
        ('Selesai', 'Selesai'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pekerjaan')  # Proyek tempat pekerjaan ini dilakukan
    nama = models.CharField(max_length=255)  # Nama pekerjaan
    deskripsi = models.TextField()  # Penjelasan tentang pekerjaan
    lokasi = models.CharField(max_length=150)  # Lokasi pekerjaan
    tanggal_mulai = models.DateField()  # Tanggal mulai pekerjaan
    tanggal_selesai = models.DateField()  # Tanggal selesai pekerjaan
    pelaksana = models.CharField(max_length=100, blank=True, null=True)  # Pelaksana pekerjaan (bisa lebih dari satu nama)
    supervisor = models.CharField(max_length=100)  # Supervisor yang bertanggung jawab atas pekerjaan
    status = models.CharField("Status Pekerjaan", max_length=20, choices=PEKERJAAN_STATUS_CHOICES, default='Perencanaan') # Menggunakan pilihan status khusus pekerjaan
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu pembuatan
    updated_at = models.DateTimeField(auto_now=True)  # Waktu terakhir diperbarui

    def __str__(self):
        return self.nama


# ===== Model Aktivitas: bagian detail dari pekerjaan, semacam to-do list-nya =====
class Aktivitas(models.Model):
    AKTIVITAS_STATUS_CHOICES = [ # Pilihan status aktivitas
        ('Perencanaan', 'Perencanaan'),
        ('Berlangsung', 'Berlangsung'),
        ('Tertunda', 'Tertunda'),
        ('Berhenti', 'Berhenti'),
        ('Selesai', 'Selesai'),
    ]
    pekerjaan = models.ForeignKey(Pekerjaan, on_delete=models.CASCADE, related_name='aktivitas')  # Pekerjaan yang memiliki aktivitas ini
    nama = models.CharField(max_length=255)  # Nama aktivitas
    waktu_pelaksanaan = models.DateField()  # Kapan aktivitas ini dijalankan
    pelaksana = models.CharField(max_length=100, blank=True, null=True)  # Pelaksana aktivitas
    status = models.CharField("Status Aktivitas", max_length=20, choices=AKTIVITAS_STATUS_CHOICES, default='Perencanaan') # Menggunakan pilihan status khusus aktivitas
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu pembuatan
    updated_at = models.DateTimeField(auto_now=True)  # Waktu update

    def __str__(self):
        return self.nama


# ===== Model PenutupanProyek: dokumentasi resmi bahwa proyek telah ditutup =====
class PenutupanProyek(models.Model):
    proyek = models.OneToOneField(Project, on_delete=models.CASCADE)  # Proyek yang ditutup
    evaluasi = models.TextField()  # Evaluasi akhir proyek
    tanda_tangan = models.FileField(upload_to='tanda_tangan/')  # File tanda tangan (PDF/gambar)
    tanggal_tutup = models.DateTimeField(auto_now_add=True)  # Waktu penutupan proyek

    def __str__(self):
        return f"Penutupan {self.proyek.name}"


# ===== Model IntegrasiPesan: menyimpan data pertukaran status antar modul lain (IE, IC, IM) =====
class IntegrasiPesan(models.Model):
    TUJUAN_CHOICES = [
        ('IE', 'Intelligence Engineering'),
        ('IC', 'Intelligence Creation'),
        ('IM', 'Implementation'),
    ]

    proyek = models.ForeignKey(Project, on_delete=models.CASCADE)  # Proyek yang dikirimkan pesannya
    tujuan = models.CharField(max_length=2, choices=TUJUAN_CHOICES)  # Tujuan pengiriman data (ke modul mana)
    dikirim = models.BooleanField(default=False)  # Apakah pesan sudah dikirim
    status_terakhir = models.CharField(max_length=100, blank=True, null=True)  # Status terakhir dari respon modul
    tanggal_dikirim = models.DateTimeField(auto_now_add=True)  # Tanggal pesan dikirim
    respon = models.TextField(blank=True, null=True)  # Isi respon dari modul yang dituju
    isi_pesan = models.TextField(blank=True, null=True)  # Isi detail pesan yang dikirim
    asal = models.CharField(
        max_length=10,
        choices=[('system', 'System'), ('external', 'External')],
        default='system'
    )  # Asal pesan: dari sistem sendiri atau eksternal
    waktu = models.DateTimeField(default=timezone.now)  # Waktu pesan dibuat

    def __str__(self):
        return f"{self.get_tujuan_display()} - {self.proyek.name}"