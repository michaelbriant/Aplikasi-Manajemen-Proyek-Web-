from rest_framework import serializers
from .models import Project, ProjectMember, Pekerjaan, Aktivitas

# ===== Serializer untuk model Aktivitas =====
class AktivitasSerializer(serializers.ModelSerializer):
    # Ubah nama field agar lebih informatif saat dikirim ke API client
    nama_aktivitas = serializers.CharField(source='nama')  # Ambil field 'nama' dari model
    waktu_pelaksanaan = serializers.DateField()  # Langsung sesuai field asli
    pelaksana_aktivitas = serializers.CharField(source='pelaksana')  # Ambil field 'pelaksana'

    class Meta:
        model = Aktivitas
        fields = [
            'nama_aktivitas',
            'waktu_pelaksanaan',
            'pelaksana_aktivitas'
        ]


# ===== Serializer untuk model Pekerjaan =====
class PekerjaanSerializer(serializers.ModelSerializer):
    nama_pekerjaan = serializers.CharField(source='nama')
    deskripsi_pekerjaan = serializers.CharField(source='deskripsi')
    lokasi = serializers.CharField()
    tanggal_mulai = serializers.DateField()
    tanggal_selesai = serializers.DateField()
    pelaksana_pekerjaan = serializers.CharField(source='pelaksana')
    supervisor_pekerjaan = serializers.CharField(source='supervisor')

    # Nested serializer → ambil semua aktivitas dalam pekerjaan ini
    aktivitas = AktivitasSerializer(many=True, read_only=True)

    class Meta:
        model = Pekerjaan
        fields = [
            'nama_pekerjaan',
            'deskripsi_pekerjaan',
            'lokasi',
            'tanggal_mulai',
            'tanggal_selesai',
            'pelaksana_pekerjaan',
            'supervisor_pekerjaan',
            'aktivitas'  # daftar aktivitas dari pekerjaan ini
        ]


# ===== Serializer untuk anggota tim dalam proyek (melalui ProjectMember) =====
class ProjectMemberSerializer(serializers.ModelSerializer):
    nama = serializers.CharField(source='member.name')  # Ambil nama dari relasi member
    jabatan = serializers.CharField(source='role')  # Ambil jabatan dari field role

    class Meta:
        model = ProjectMember
        fields = [
            'nama',
            'jabatan'
        ]


# ===== Serializer utama untuk Project (tampilkan semua info termasuk nested) =====
class ProjectSerializer(serializers.ModelSerializer):
    nama_proyek = serializers.CharField(source='name')
    deskripsi_proyek = serializers.CharField(source='description')
    lokasi = serializers.CharField(source='location')
    tanggal_mulai = serializers.DateField(source='start_date')
    tanggal_selesai = serializers.DateField(source='end_date')
    supervisor_proyek = serializers.CharField(source='supervisor')

    # Ambil semua pelaksana proyek (melalui relasi projectmember_set)
    pelaksana_proyek = ProjectMemberSerializer(source='projectmember_set', many=True)

    # Ambil pekerjaan-pekerjaan dalam proyek (beserta aktivitas di dalamnya)
    pekerjaan = PekerjaanSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'nama_proyek',
            'deskripsi_proyek',
            'lokasi',
            'tanggal_mulai',
            'tanggal_selesai',
            'supervisor_proyek',
            'status',
            'pelaksana_proyek',
            'pekerjaan'
        ]


# ===== Serializer versi ringkas untuk hanya menampilkan status proyek =====
class ProjectStatusOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'supervisor', 'status']  # Versi minimal untuk status monitoring
