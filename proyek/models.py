from django.db import models

class TeamMember(models.Model):
    GENDER_CHOICES = [
        ('L', 'Laki - Laki'),
        ('P', 'Perempuan'),
    ]

    name = models.CharField(max_length=100)
    birth_date = models.DateField("Tanggal Lahir", blank=True, null=True)
    address = models.CharField("Alamat", max_length=255, blank=True, null=True)
    gender = models.CharField("Jenis Kelamin", max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    skills = models.TextField("Keahlian", blank=True, null=True)
    role = models.CharField("Peran", max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField("Nama Proyek", max_length=200)
    description = models.TextField("Deskripsi Singkat Proyek")
    location = models.CharField("Lokasi", max_length=150)
    start_date = models.DateField("Tanggal Mulai")
    end_date = models.DateField("Tanggal Selesai")
    supervisor = models.CharField("Supervisor", max_length=100)

    members = models.ManyToManyField(TeamMember, blank=True, related_name='projects')

    def __str__(self):
        return self.name

class AktivitasPekerjaan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField("Nama Aktivitas", max_length=200)
    time = models.DateField("Waktu Aktivitas")
    planner = models.CharField("Perancang Aktivitas", max_length=100)
    notes = models.FileField("Catatan Aktivitas", upload_to='aktivitas/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.project.name})"
