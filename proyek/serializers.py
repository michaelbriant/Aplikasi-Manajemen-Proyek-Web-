from rest_framework import serializers
from .models import Project, ProjectMember, Pekerjaan, Aktivitas


class AktivitasSerializer(serializers.ModelSerializer):
    nama_aktivitas = serializers.CharField(source='nama')
    waktu_pelaksanaan = serializers.DateField()
    pelaksana_aktivitas = serializers.CharField(source='pelaksana')

    class Meta:
        model = Aktivitas
        fields = [
            'nama_aktivitas',
            'waktu_pelaksanaan',
            'pelaksana_aktivitas'
        ]


class PekerjaanSerializer(serializers.ModelSerializer):
    nama_pekerjaan = serializers.CharField(source='nama')
    deskripsi_pekerjaan = serializers.CharField(source='deskripsi')
    lokasi = serializers.CharField()
    tanggal_mulai = serializers.DateField()
    tanggal_selesai = serializers.DateField()
    pelaksana_pekerjaan = serializers.CharField(source='pelaksana')
    supervisor_pekerjaan = serializers.CharField(source='supervisor')
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
            'aktivitas'
        ]


class ProjectMemberSerializer(serializers.ModelSerializer):
    nama = serializers.CharField(source='member.name')
    jabatan = serializers.CharField(source='role')

    class Meta:
        model = ProjectMember
        fields = [
            'nama',
            'jabatan'
        ]


class ProjectSerializer(serializers.ModelSerializer):
    nama_proyek = serializers.CharField(source='name')
    deskripsi_proyek = serializers.CharField(source='description')
    lokasi = serializers.CharField(source='location')
    tanggal_mulai = serializers.DateField(source='start_date')
    tanggal_selesai = serializers.DateField(source='end_date')
    supervisor_proyek = serializers.CharField(source='supervisor')
    pelaksana_proyek = ProjectMemberSerializer(source='projectmember_set', many=True)
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


class ProjectStatusOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'supervisor', 'status']