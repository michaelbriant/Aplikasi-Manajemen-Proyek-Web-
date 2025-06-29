from rest_framework import serializers
from .models import Project, ProjectMember, Pekerjaan, Aktivitas, TeamMember

# Serializer untuk model Aktivitas
class AktivitasSerializer(serializers.ModelSerializer):
    nama_aktivitas = serializers.CharField(source='nama', required=False, allow_blank=True)
    waktu_pelaksanaan = serializers.DateField(required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    pelaksana_aktivitas = serializers.CharField(source='pelaksana', required=False, allow_blank=True)
    status_aktivitas = serializers.CharField(source='status', required=False, allow_blank=True)

    class Meta:
        model = Aktivitas
        fields = [
            'id', # ID Aktivitas
            'nama_aktivitas',
            'waktu_pelaksanaan',
            'pelaksana_aktivitas',
            'status_aktivitas',
        ]


# Serializer untuk model Pekerjaan
class PekerjaanSerializer(serializers.ModelSerializer):
    nama_pekerjaan = serializers.CharField(source='nama', required=False, allow_blank=True)
    deskripsi_pekerjaan = serializers.CharField(source='deskripsi', required=False, allow_blank=True)
    lokasi = serializers.CharField(required=False, allow_blank=True)
    tanggal_mulai = serializers.DateField(required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    tanggal_selesai = serializers.DateField(required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    pelaksana_pekerjaan = serializers.CharField(source='pelaksana', required=False, allow_blank=True)
    supervisor_pekerjaan = serializers.CharField(source='supervisor', required=False, allow_blank=True)
    status_pekerjaan = serializers.CharField(source='status', required=False, allow_blank=True)
    aktivitas = AktivitasSerializer(many=True, read_only=True) # Biarkan read_only=True jika aktivitas tidak dikirim saat membuat/mengubah Pekerjaan

    class Meta:
        model = Pekerjaan
        fields = [
            'id', # ID Pekerjaan
            'nama_pekerjaan',
            'deskripsi_pekerjaan',
            'lokasi',
            'tanggal_mulai',
            'tanggal_selesai',
            'pelaksana_pekerjaan',
            'supervisor_pekerjaan',
            'status_pekerjaan',
            'aktivitas', # Daftar aktivitas terkait pekerjaan (hanya untuk dibaca)
        ]


class ProjectMemberWriteSerializer(serializers.Serializer):
    nama = serializers.CharField(required=True)
    jabatan = serializers.CharField(required=True)


# Serializer utama untuk Project
class ProjectSerializer(serializers.ModelSerializer):
    nama_proyek = serializers.CharField(source='name', required=False, allow_blank=True)
    deskripsi_proyek = serializers.CharField(source='description', required=False, allow_blank=True)
    lokasi = serializers.CharField(source='location', required=False, allow_blank=True)
    # Tambahkan input_formats untuk tanggal agar bisa memparsing format dd/MM/yyyy dari Android
    tanggal_mulai = serializers.DateField(source='start_date', required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    tanggal_selesai = serializers.DateField(source='end_date', required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    supervisor_proyek = serializers.CharField(source='supervisor', required=False, allow_blank=True)
    status_proyek = serializers.CharField(source='status', required=False, allow_blank=True)

    pelaksana_proyek = ProjectMemberWriteSerializer(many=True, write_only=True, required=False)

    project_members_output = serializers.SerializerMethodField()

    def get_project_members_output(self, obj):
        # Mengambil ProjectMember yang terkait dengan proyek ini
        project_members = obj.projectmember_set.all()
        # Mengubahnya ke format yang Anda kirim dari Android atau format yang lebih mudah dibaca
        # Ini hanya untuk respons API GET
        return [{"nama": pm.member.name, "jabatan": pm.role} for pm in project_members]

    pekerjaan = PekerjaanSerializer(many=True)

    class Meta:
        model = Project
        fields = [
            'id', # ID Proyek
            'nama_proyek',
            'deskripsi_proyek',
            'lokasi',
            'tanggal_mulai',
            'tanggal_selesai',
            'supervisor_proyek',
            'status_proyek',
            'pelaksana_proyek',
            'project_members_output',
            'pekerjaan',
        ]


    def create(self, validated_data):
        pelaksana_data_for_write = validated_data.pop('pelaksana_proyek', [])
        pekerjaan_data = validated_data.pop('pekerjaan', [])

        project = Project.objects.create(**validated_data)

        for member_item in pelaksana_data_for_write:
            try:
                member = TeamMember.objects.get(name=member_item['nama'])
                ProjectMember.objects.create(
                    project=project,
                    member=member,
                    role=member_item['jabatan']
                )
            except TeamMember.DoesNotExist:
                raise serializers.ValidationError(f"Anggota tim dengan nama '{member_item['nama']}' tidak ditemukan.")
            except Exception as e:
                raise serializers.ValidationError(f"Gagal menambahkan pelaksana: {e}")

        for pekerjaan_item in pekerjaan_data:
            aktivitas_data = pekerjaan_item.pop('aktivitas', [])  # Diabaikan
            Pekerjaan.objects.create(
                project=project,
                nama=pekerjaan_item.get('nama_pekerjaan', ''),
                deskripsi=pekerjaan_item.get('deskripsi_pekerjaan', ''),
                lokasi=pekerjaan_item.get('lokasi', ''),
                tanggal_mulai=pekerjaan_item.get('tanggal_mulai'),
                tanggal_selesai=pekerjaan_item.get('tanggal_selesai'),
                pelaksana=pekerjaan_item.get('pelaksana_pekerjaan', ''),
                supervisor=pekerjaan_item.get('supervisor_pekerjaan', ''),
                status=pekerjaan_item.get('status_pekerjaan', '')
            )

        return project

    def update(self, instance, validated_data):
        pelaksana_data_for_write = validated_data.pop('pelaksana_proyek', None)
        pekerjaan_data = validated_data.pop('pekerjaan', None)

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.supervisor = validated_data.get('supervisor', instance.supervisor)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if pelaksana_data_for_write is not None:
            instance.projectmember_set.all().delete()
            for member_item in pelaksana_data_for_write:
                try:
                    member = TeamMember.objects.get(name=member_item['nama'])
                    ProjectMember.objects.create(
                        project=instance,
                        member=member,
                        role=member_item['jabatan']
                    )
                except TeamMember.DoesNotExist:
                    raise serializers.ValidationError(f"Anggota tim dengan nama '{member_item['nama']}' tidak ditemukan.")
                except Exception as e:
                    raise serializers.ValidationError(f"Gagal memperbarui pelaksana: {e}")

        if pekerjaan_data is not None:
            instance.pekerjaan.all().delete()
            for pekerjaan_item in pekerjaan_data:
                aktivitas_data = pekerjaan_item.pop('aktivitas', [])
                Pekerjaan.objects.create(
                    project=instance,
                    nama=pekerjaan_item.get('nama_pekerjaan', ''),
                    deskripsi=pekerjaan_item.get('deskripsi_pekerjaan', ''),
                    lokasi=pekerjaan_item.get('lokasi', ''),
                    tanggal_mulai=pekerjaan_item.get('tanggal_mulai'),
                    tanggal_selesai=pekerjaan_item.get('tanggal_selesai'),
                    pelaksana=pekerjaan_item.get('pelaksana_pekerjaan', ''),
                    supervisor=pekerjaan_item.get('supervisor_pekerjaan', ''),
                    status=pekerjaan_item.get('status_pekerjaan', '')
                )

        return instance

# Serializer ringkas untuk hanya menampilkan status proyek
class ProjectStatusOnlySerializer(serializers.ModelSerializer):
    nama_proyek = serializers.CharField(source='name', read_only=True)
    supervisor_proyek = serializers.CharField(source='supervisor', read_only=True)
    status_proyek = serializers.CharField(source='status', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'nama_proyek', 'supervisor_proyek', 'status_proyek']