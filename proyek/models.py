from django.db import models
from django.utils import timezone

# ===== Model Anggota Tim: untuk menyimpan informasi setiap anggota tim proyek =====
class TeamMember(models.Model):
    """
    Model ini merepresentasikan seorang anggota tim yang dapat terlibat dalam berbagai proyek.
    Menyimpan detail pribadi dan profesional anggota tim.
    """
    GENDER_CHOICES = [  # Pilihan untuk jenis kelamin
        ('L', 'Laki - Laki'),
        ('P', 'Perempuan'),
    ]

    name = models.CharField(max_length=100)  # Nama lengkap anggota
    birth_date = models.DateField("Tanggal Lahir", blank=True, null=True)  # Tanggal lahir (opsional), bisa kosong
    gender = models.CharField("Jenis Kelamin", max_length=1, choices=GENDER_CHOICES, blank=True, null=True)  # Jenis kelamin (opsional), pilihan terbatas
    skills = models.TextField("Deskripsi Kompetensi", blank=True, null=True)  # Daftar skill atau kompetensi (opsional)
    role = models.TextField("Deskripsi Pengalaman", blank=True, null=True)  # Deskripsi pengalaman atau peran (opsional)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)  # Foto profil (opsional), diunggah ke direktori 'photos/'
    created_at = models.DateTimeField(auto_now_add=True)  # Tanggal dan waktu data dibuat otomatis saat pertama kali disimpan
    updated_at = models.DateTimeField(auto_now=True)  # Tanggal dan waktu data terakhir diperbarui otomatis setiap kali disimpan

    def __str__(self):
        """
        Representasi string dari objek TeamMember.
        Akan menampilkan nama anggota tim.
        """
        return self.name


# ===== Model Proyek: untuk menyimpan informasi proyek secara keseluruhan =====
class Project(models.Model):
    """
    Model ini merepresentasikan sebuah proyek secara keseluruhan,
    termasuk detail, status, dan informasi terkait penutupan proyek.
    """
    STATUS_CHOICES = [  # Pilihan status proyek yang tersedia
        ('Perencanaan', 'Perencanaan'),
        ('Berlangsung', 'Berlangsung'),
        ('Tertunda', 'Tertunda'),
        ('Berhenti', 'Berhenti'),
        ('siap_dideploy', 'Siap untuk Dideploy'),
        ('Selesai', 'Selesai'),
    ]

    name = models.CharField("Nama Proyek", max_length=200)  # Nama proyek, wajib diisi
    description = models.TextField("Deskripsi Singkat Proyek")  # Ringkasan tentang proyek, wajib diisi
    location = models.CharField("Lokasi", max_length=150)  # Lokasi pelaksanaan proyek, wajib diisi
    start_date = models.DateField("Tanggal Mulai")  # Tanggal mulai proyek, wajib diisi
    end_date = models.DateField("Tanggal Selesai")  # Tanggal akhir proyek, wajib diisi
    supervisor = models.CharField("Supervisor", max_length=100)  # Nama supervisor proyek, wajib diisi
    status = models.CharField("Status Proyek", max_length=20, choices=STATUS_CHOICES, default='Perencanaan')  # Status saat ini proyek, dengan pilihan terbatas dan default 'Perencanaan'
    # Many-to-many relationship dengan TeamMember melalui model perantara ProjectMember.
    # `blank=True` berarti proyek dapat tidak memiliki anggota.
    members = models.ManyToManyField('TeamMember', through='ProjectMember', blank=True)
    final_evaluation = models.TextField("Evaluasi Akhir", blank=True, null=True)  # Evaluasi akhir proyek (opsional)
    final_report = models.FileField("Laporan Akhir", upload_to='laporan_akhir/', blank=True, null=True)  # File laporan akhir proyek (opsional), diunggah ke 'laporan_akhir/'
    supervisor_signed = models.BooleanField("Ditandatangani Supervisor", default=False)  # Menandakan apakah supervisor telah menandatangani (default False)
    owner_signed = models.BooleanField("Ditandatangani Pemilik Proyek", default=False)  # Menandakan apakah pemilik proyek telah menandatangani (default False)
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu pembuatan otomatis
    updated_at = models.DateTimeField(auto_now=True)  # Waktu terakhir diperbarui otomatis

    def __str__(self):
        """
        Representasi string dari objek Project.
        Akan menampilkan nama proyek.
        """
        return self.name


# ===== Model Perantara ProjectMember: untuk menghubungkan Project dan TeamMember dengan peran khusus =====
class ProjectMember(models.Model):
    """
    Model perantara (through model) ini menghubungkan model `Project` dan `TeamMember`.
    Ini memungkinkan untuk mendefinisikan peran spesifik seorang anggota tim dalam proyek tertentu.
    """
    project = models.ForeignKey('Project', on_delete=models.CASCADE)  # Proyek terkait, jika proyek dihapus, relasi ini juga dihapus
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)  # Anggota tim terkait, jika anggota dihapus, relasi ini juga dihapus
    role = models.CharField("Peran", max_length=100)  # Peran anggota dalam proyek (misal: developer, analis, desainer, dst.)

    def __str__(self):
        """
        Representasi string dari objek ProjectMember.
        Akan menampilkan nama anggota dan perannya dalam proyek.
        """
        return f"{self.member.name} - {self.role}"


# ===== Model Pekerjaan: untuk menyimpan daftar pekerjaan dalam suatu proyek =====
class Pekerjaan(models.Model):
    """
    Model ini merepresentasikan sebuah pekerjaan atau tugas besar dalam suatu proyek.
    Setiap pekerjaan terkait dengan satu proyek.
    """
    PEKERJAAN_STATUS_CHOICES = [ # Pilihan status khusus untuk Pekerjaan
        ('Perencanaan', 'Perencanaan'),
        ('Berlangsung', 'Berlangsung'),
        ('Tertunda', 'Tertunda'),
        ('Berhenti', 'Berhenti'),
        ('Selesai', 'Selesai'),
    ]
    # Foreign key ke model Project, jika proyek dihapus, pekerjaan ini juga dihapus.
    # `related_name='pekerjaan'` memungkinkan akses balik dari Project ke Pekerjaan (e.g., `project.pekerjaan.all()`).
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pekerjaan')
    nama = models.CharField(max_length=255)  # Nama pekerjaan, wajib diisi
    deskripsi = models.TextField()  # Penjelasan detail tentang pekerjaan, wajib diisi
    lokasi = models.CharField(max_length=150)  # Lokasi pelaksanaan pekerjaan, wajib diisi
    tanggal_mulai = models.DateField()  # Tanggal mulai pekerjaan, wajib diisi
    tanggal_selesai = models.DateField()  # Tanggal selesai pekerjaan, wajib diisi
    pelaksana = models.CharField(max_length=100, blank=True, null=True)  # Pelaksana pekerjaan (bisa lebih dari satu nama, disimpan sebagai string), opsional
    supervisor = models.CharField(max_length=100)  # Supervisor yang bertanggung jawab atas pekerjaan, wajib diisi
    status = models.CharField("Status Pekerjaan", max_length=20, choices=PEKERJAAN_STATUS_CHOICES, default='Perencanaan') # Status saat ini pekerjaan, dengan pilihan terbatas dan default 'Perencanaan'
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu pembuatan otomatis
    updated_at = models.DateTimeField(auto_now=True)  # Waktu terakhir diperbarui otomatis

    def __str__(self):
        """
        Representasi string dari objek Pekerjaan.
        Akan menampilkan nama pekerjaan.
        """
        return self.nama


# ===== Model Aktivitas: bagian detail dari pekerjaan, semacam to-do list-nya =====
class Aktivitas(models.Model):
    """
    Model ini merepresentasikan sebuah aktivitas atau tugas yang lebih kecil
    dan spesifik yang merupakan bagian dari sebuah Pekerjaan.
    """
    AKTIVITAS_STATUS_CHOICES = [ # Pilihan status khusus untuk Aktivitas
        ('Perencanaan', 'Perencanaan'),
        ('Berlangsung', 'Berlangsung'),
        ('Tertunda', 'Tertunda'),
        ('Berhenti', 'Berhenti'),
        ('Selesai', 'Selesai'),
    ]
    # Foreign key ke model Pekerjaan, jika pekerjaan dihapus, aktivitas ini juga dihapus.
    # `related_name='aktivitas'` memungkinkan akses balik dari Pekerjaan ke Aktivitas (e.g., `pekerjaan.aktivitas.all()`).
    pekerjaan = models.ForeignKey(Pekerjaan, on_delete=models.CASCADE, related_name='aktivitas')
    nama = models.CharField(max_length=255)  # Nama aktivitas, wajib diisi
    waktu_pelaksanaan = models.DateField()  # Kapan aktivitas ini dijalankan (tanggal), wajib diisi
    pelaksana = models.CharField(max_length=100, blank=True, null=True)  # Pelaksana aktivitas (bisa lebih dari satu nama), opsional
    status = models.CharField("Status Aktivitas", max_length=20, choices=AKTIVITAS_STATUS_CHOICES, default='Perencanaan') # Status saat ini aktivitas, dengan pilihan terbatas dan default 'Perencanaan'
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu pembuatan otomatis
    updated_at = models.DateTimeField(auto_now=True)  # Waktu terakhir diperbarui otomatis

    def __str__(self):
        """
        Representasi string dari objek Aktivitas.
        Akan menampilkan nama aktivitas.
        """
        return self.nama


# ===== Model PenutupanProyek: dokumentasi resmi bahwa proyek telah ditutup =====
class PenutupanProyek(models.Model):
    """
    Model ini mencatat informasi resmi terkait penutupan sebuah proyek.
    Memiliki relasi One-to-One dengan model Project.
    """
    # One-to-one relationship dengan model Project.
    # Jika proyek dihapus, entri penutupan proyek ini juga dihapus.
    proyek = models.OneToOneField(Project, on_delete=models.CASCADE)
    evaluasi = models.TextField()  # Evaluasi akhir proyek, wajib diisi
    tanda_tangan = models.FileField(upload_to='tanda_tangan/')  # File tanda tangan (PDF/gambar), diunggah ke 'tanda_tangan/'
    tanggal_tutup = models.DateTimeField(auto_now_add=True)  # Waktu penutupan proyek, diisi otomatis

    def __str__(self):
        """
        Representasi string dari objek PenutupanProyek.
        Akan menampilkan "Penutupan [Nama Proyek]".
        """
        return f"Penutupan {self.proyek.name}"


# ===== Model IntegrasiPesan: menyimpan data pertukaran status antar modul lain (IE, IC, IM) =====
class IntegrasiPesan(models.Model):
    """
    Model ini berfungsi untuk mencatat log pertukaran pesan atau status
    antara modul sistem ini dengan modul eksternal (IE, IC, IM).
    """
    TUJUAN_CHOICES = [ # Pilihan modul tujuan pesan
        ('IE', 'Intelligence Engineering'),==
        ('IC', 'Intelligence Creation'),
        ('IM', 'Implementation'),
    ]

    proyek = models.ForeignKey(Project, on_delete=models.CASCADE)  # Proyek yang terkait dengan pesan ini
    tujuan = models.CharField(max_length=2, choices=TUJUAN_CHOICES)  # Tujuan pengiriman data (ke modul mana)
    dikirim = models.BooleanField(default=False)  # Status pengiriman: True jika sudah dikirim, False jika belum (default False)
    status_terakhir = models.CharField(max_length=100, blank=True, null=True)  # Status terakhir dari respon modul tujuan (opsional)
    tanggal_dikirim = models.DateTimeField(auto_now_add=True)  # Tanggal dan waktu pesan dikirim otomatis
    respon = models.TextField(blank=True, null=True)  # Isi respon yang diterima dari modul tujuan (opsional)
    isi_pesan = models.TextField(blank=True, null=True)  # Isi detail pesan yang dikirim (payload JSON, dll.) (opsional)
    asal = models.CharField( # Asal pesan: 'system' (dari aplikasi ini) atau 'external' (dari luar)
        max_length=10,
        choices=[('system', 'System'), ('external', 'External')],
        default='system'
    )
    waktu = models.DateTimeField(default=timezone.now)  # Waktu pesan dibuat (default waktu saat ini)

    def __str__(self):
        """
        Representasi string dari objek IntegrasiPesan.
        Akan menampilkan tujuan pesan dan nama proyek yang terkait.
        """
        return f"{self.get_tujuan_display()} - {self.proyek.name}"