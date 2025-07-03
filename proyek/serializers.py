from rest_framework import serializers
from .models import Project, ProjectMember, Pekerjaan, Aktivitas, TeamMember

# Serializer untuk model Aktivitas
class AktivitasSerializer(serializers.ModelSerializer):
    """
    Serializer untuk model Aktivitas.
    Mengatur bagaimana data Aktivitas dikonversi antara format Python dan representasi JSON.
    Menggunakan field kustom untuk pemetaan nama field dan format tanggal.
    """
    # Memetakan field 'nama' dari model Aktivitas ke 'nama_aktivitas' di API
    nama_aktivitas = serializers.CharField(source='nama', required=False, allow_blank=True)
    # Memetakan field 'waktu_pelaksanaan' dengan format tanggal spesifik (DD/MM/YYYY)
    waktu_pelaksanaan = serializers.DateField(required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    # Memetakan field 'pelaksana' dari model Aktivitas ke 'pelaksana_aktivitas' di API
    pelaksana_aktivitas = serializers.CharField(source='pelaksana', required=False, allow_blank=True)
    # Memetakan field 'status' dari model Aktivitas ke 'status_aktivitas' di API
    status_aktivitas = serializers.CharField(source='status', required=False, allow_blank=True)

    class Meta:
        """
        Meta class untuk mengkonfigurasi serializer.
        Menentukan model yang terkait dan field yang akan disertakan dalam serialisasi.
        """
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
    """
    Serializer untuk model Pekerjaan.
    Mengatur bagaimana data Pekerjaan dikonversi.
    Juga menyertakan nested serializer untuk daftar Aktivitas yang terkait.
    """
    # Memetakan field 'nama' dari model Pekerjaan ke 'nama_pekerjaan' di API
    nama_pekerjaan = serializers.CharField(source='nama', required=False, allow_blank=True)
    # Memetakan field 'deskripsi' dari model Pekerjaan ke 'deskripsi_pekerjaan' di API
    deskripsi_pekerjaan = serializers.CharField(source='deskripsi', required=False, allow_blank=True)
    lokasi = serializers.CharField(required=False, allow_blank=True)
    # Memetakan field 'tanggal_mulai' dengan format tanggal spesifik
    tanggal_mulai = serializers.DateField(required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    # Memetakan field 'tanggal_selesai' dengan format tanggal spesifik
    tanggal_selesai = serializers.DateField(required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    # Memetakan field 'pelaksana' dari model Pekerjaan ke 'pelaksana_pekerjaan' di API
    pelaksana_pekerjaan = serializers.CharField(source='pelaksana', required=False, allow_blank=True)
    # Memetakan field 'supervisor' dari model Pekerjaan ke 'supervisor_pekerjaan' di API
    supervisor_pekerjaan = serializers.CharField(source='supervisor', required=False, allow_blank=True)
    # Memetakan field 'status' dari model Pekerjaan ke 'status_pekerjaan' di API
    status_pekerjaan = serializers.CharField(source='status', required=False, allow_blank=True)
    # Nested serializer untuk Aktivitas. `many=True` karena ada banyak aktivitas per pekerjaan.
    # `read_only=True` berarti aktivitas tidak akan dibuat/diperbarui melalui serializer ini saat POST/PUT Pekerjaan.
    aktivitas = AktivitasSerializer(many=True, read_only=True)

    class Meta:
        """
        Meta class untuk mengkonfigurasi serializer.
        Menentukan model yang terkait dan field yang akan disertakan dalam serialisasi.
        """
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
    """
    Serializer khusus yang digunakan untuk menerima data anggota proyek saat operasi penulisan (create/update)
    pada ProjectSerializer. Ini tidak terikat langsung ke model.
    """
    nama = serializers.CharField(required=True)
    jabatan = serializers.CharField(required=True)


# Serializer utama untuk Project
class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer utama untuk model Project.
    Mengatur konversi data Project, termasuk nested data untuk Pekerjaan dan anggota proyek.
    Menyediakan logika kustom untuk operasi create dan update.
    """
    # Memetakan field 'name' dari model Project ke 'nama_proyek' di API
    nama_proyek = serializers.CharField(source='name', required=False, allow_blank=True)
    # Memetakan field 'description' dari model Project ke 'deskripsi_proyek' di API
    deskripsi_proyek = serializers.CharField(source='description', required=False, allow_blank=True)
    # Memetakan field 'location' dari model Project ke 'lokasi' di API
    lokasi = serializers.CharField(source='location', required=False, allow_blank=True)
    # Memetakan field 'start_date' dengan format tanggal spesifik.
    # Menambahkan `input_formats` agar dapat memparsing format "dd/MM/yyyy" dari klien (misal Android).
    tanggal_mulai = serializers.DateField(source='start_date', required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    # Memetakan field 'end_date' dengan format tanggal spesifik.
    tanggal_selesai = serializers.DateField(source='end_date', required=False, format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    # Memetakan field 'supervisor' dari model Project ke 'supervisor_proyek' di API
    supervisor_proyek = serializers.CharField(source='supervisor', required=False, allow_blank=True)
    # Memetakan field 'status' dari model Project ke 'status_proyek' di API
    status_proyek = serializers.CharField(source='status', required=False, allow_blank=True)

    # Field untuk menerima data anggota tim saat membuat/memperbarui proyek.
    # `many=True` karena bisa ada banyak anggota.
    # `write_only=True` berarti field ini hanya digunakan untuk input (tidak akan muncul di output GET).
    # `required=False` agar anggota tim bersifat opsional.
    pelaksana_proyek = ProjectMemberWriteSerializer(many=True, write_only=True, required=False)

    # Field `SerializerMethodField` untuk mengelola representasi output anggota proyek.
    # Ini akan memformat data ProjectMember yang terkait menjadi bentuk yang lebih mudah dibaca saat GET request.
    project_members_output = serializers.SerializerMethodField()

    def get_project_members_output(self, obj):
        """
        Metode untuk mengembalikan daftar anggota proyek dengan nama dan jabatan mereka.
        Digunakan untuk output serialisasi (saat GET request).
        """
        # Mengambil semua ProjectMember yang terkait dengan instance proyek saat ini (obj)
        project_members = obj.projectmember_set.all()
        # Mengubah queryset ProjectMember menjadi list dictionary dengan 'nama' dan 'jabatan'
        return [{"nama": pm.member.name, "jabatan": pm.role} for pm in project_members]

    # Nested serializer untuk daftar Pekerjaan.
    # Ketika `many=True`, serializer ini akan menangani daftar objek Pekerjaan.
    # Pekerjaan dapat dibuat/diperbarui melalui serializer Project ini.
    pekerjaan = PekerjaanSerializer(many=True)

    class Meta:
        """
        Meta class untuk mengkonfigurasi serializer Project.
        Menentukan model Project dan field yang akan disertakan dalam serialisasi.
        """
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
            'pelaksana_proyek',        # Digunakan untuk input (write-only)
            'project_members_output',  # Digunakan untuk output (read-only)
            'pekerjaan',               # Nested serializer untuk pekerjaan
        ]

    def create(self, validated_data):
        """
        Metode kustom untuk membuat instance Project dan objek terkaitnya (ProjectMember, Pekerjaan).
        `validated_data` berisi data yang sudah divalidasi dari request.
        """
        # Pop data pelaksana dan pekerjaan karena akan ditangani secara terpisah
        pelaksana_data_for_write = validated_data.pop('pelaksana_proyek', [])
        pekerjaan_data = validated_data.pop('pekerjaan', [])

        # Buat objek Project utama
        project = Project.objects.create(**validated_data)

        # Iterasi dan buat ProjectMember untuk setiap pelaksana yang diberikan
        for member_item in pelaksana_data_for_write:
            try:
                # Cari TeamMember berdasarkan nama
                member = TeamMember.objects.get(name=member_item['nama'])
                # Buat relasi ProjectMember
                ProjectMember.objects.create(
                    project=project,
                    member=member,
                    role=member_item['jabatan']
                )
            except TeamMember.DoesNotExist:
                # Tangani jika anggota tim tidak ditemukan
                raise serializers.ValidationError(f"Anggota tim dengan nama '{member_item['nama']}' tidak ditemukan.")
            except Exception as e:
                # Tangani error umum saat menambahkan pelaksana
                raise serializers.ValidationError(f"Gagal menambahkan pelaksana: {e}")

        # Iterasi dan buat Pekerjaan untuk proyek ini
        for pekerjaan_item in pekerjaan_data:
            # Data aktivitas diabaikan di sini karena PekerjaanSerializer memiliki `read_only=True` untuk aktivitas
            aktivitas_data = pekerjaan_item.pop('aktivitas', [])
            Pekerjaan.objects.create(
                project=project, # Kaitkan pekerjaan dengan proyek yang baru dibuat
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
        """
        Metode kustom untuk memperbarui instance Project dan objek terkaitnya (ProjectMember, Pekerjaan).
        `instance` adalah objek Project yang akan diperbarui.
        `validated_data` berisi data yang sudah divalidasi dari request.
        """
        # Pop data pelaksana dan pekerjaan untuk penanganan terpisah
        pelaksana_data_for_write = validated_data.pop('pelaksana_proyek', None)
        pekerjaan_data = validated_data.pop('pekerjaan', None)

        # Perbarui field-field dasar Project
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.supervisor = validated_data.get('supervisor', instance.supervisor)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        # Tangani pembaruan anggota proyek jika data disediakan
        if pelaksana_data_for_write is not None:
            # Hapus semua anggota proyek yang ada
            instance.projectmember_set.all().delete()
            # Buat kembali relasi ProjectMember berdasarkan data baru
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

        # Tangani pembaruan pekerjaan proyek jika data disediakan
        if pekerjaan_data is not None:
            # Hapus semua pekerjaan yang ada
            instance.pekerjaan.all().delete()
            # Buat kembali pekerjaan berdasarkan data baru
            for pekerjaan_item in pekerjaan_data:
                # Data aktivitas diabaikan, sama seperti di metode create
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
    """
    Serializer ini dirancang untuk memberikan representasi ringkas dari model Project,
    hanya menampilkan ID, nama proyek, supervisor, dan status.
    Digunakan untuk endpoint API yang hanya membutuhkan informasi ringkasa.
    """
    # Memetakan field 'name' dari model Project ke 'nama_proyek' di API (hanya untuk dibaca)
    nama_proyek = serializers.CharField(source='name', read_only=True)
    # Memetakan field 'supervisor' dari model Project ke 'supervisor_proyek' di API (hanya untuk dibaca)
    supervisor_proyek = serializers.CharField(source='supervisor', read_only=True)
    # Memetakan field 'status' dari model Project ke 'status_proyek' di API (hanya untuk dibaca)
    status_proyek = serializers.CharField(source='status', read_only=True)

    class Meta:
        """
        Meta class untuk mengkonfigurasi serializer.
        Menentukan model Project dan field yang akan disertakan dalam serialisasi.
        """
        model = Project
        fields = ['id', 'nama_proyek', 'supervisor_proyek', 'status_proyek']