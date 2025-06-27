# ====== IMPORT DARI DJANGO & LIB TAMBAHAN ======
from django.shortcuts import render, redirect, get_object_or_404   # Untuk render template HTML, redirect URL, dan ambil objek dari DB atau beri 404 jika tidak ada
from django.contrib import messages   # Untuk menampilkan pesan notifikasi (sukses, error, dll)
from django.contrib.auth import authenticate, login, logout   # Fungsi login/logout & verifikasi user
from django.contrib.auth.decorators import login_required   # Dekorator untuk membatasi akses hanya untuk user yang login
from django.contrib.auth.models import User   # Model User bawaan Django
from django.contrib.auth.forms import SetPasswordForm   # Form bawaan Django untuk set ulang password

from django.views.decorators.http import require_POST   # Membatasi agar view hanya menerima method POST
from django.views.decorators.csrf import csrf_exempt   # Menonaktifkan CSRF protection (gunakan hati-hati)
from django.http import JsonResponse   # Untuk mengirim response berupa JSON

# ====== IMPORT MODEL, FORM, SERIALIZER APLIKASI SENDIRI ======
from .models import (
    Project, TeamMember, ProjectMember, Pekerjaan,
    Aktivitas, PenutupanProyek, IntegrasiPesan
)
from .forms import (
    ProjectForm, TeamMemberForm, PekerjaanForm,
    AktivitasForm, CustomUserCreationForm,
    TutupProyekForm, CustomSetPasswordForm
)
from .serializers import (
    ProjectSerializer, ProjectStatusOnlySerializer
)

# ====== LIB TAMBAHAN UNTUK FILE, TANGGAL, FORMAT DATA ======
from django.template.loader import render_to_string   # Render HTML ke string (misalnya untuk email/template dinamis)
from django.core.files.base import ContentFile   # Untuk menangani file upload berbasis data (seperti Base64)
from django.utils.dateformat import DateFormat   # Format tanggal
from django.utils.formats import get_format   # Ambil format lokal
from django.core.serializers.json import DjangoJSONEncoder   # JSON encoder yang support format Django (tanggal, dst)
from django.db.models import Q, Min, Max   # Untuk query filter dan agregasi

from datetime import datetime, date   # Manipulasi waktu standar
import base64   # Untuk decoding file base64 (misal foto)
import json   # Untuk parsing JSON
import requests   # Untuk akses API eksternal (integrasi)

# ====== REST FRAMEWORK UNTUK API VIEW & ENDPOINT ======
from rest_framework import viewsets   # Untuk membuat ViewSet REST
from rest_framework.views import APIView   # APIView berbasis class
from rest_framework.response import Response   # Format response REST
from rest_framework.decorators import action   # Tambahan action kustom di ViewSet
from rest_framework import permissions # <--- TAMBAHAN: Untuk mengelola izin

# ====== LANDING PAGE ======
def landing_page(request):
    # Menampilkan halaman landing.html (beranda publik sebelum login)
    return render(request, 'proyek/landing.html')

# ====== LOGOUT ======
def custom_logout(request):
    # Fungsi logout untuk mengakhiri sesi pengguna
    logout(request)
    return redirect('landing')   # Arahkan kembali ke halaman utama

# ====== REGISTRASI ======
def register(request):
    # Registrasi akun baru menggunakan form kustom
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()   # Simpan user ke database
            return redirect('login')   # Setelah berhasil daftar, arahkan ke login
    else:
        form = CustomUserCreationForm()   # Form kosong jika GET
    return render(request, 'proyek/register.html', {'form': form})

# ====== LOGIN VIEW ======
def login_view(request):
    # Fungsi login: menerima username & password lalu login
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)   # Verifikasi user
        if user:
            login(request, user)   # Jika valid, login user
            return redirect('homepage')   # Arahkan ke halaman utama
        else:
            messages.error(request, 'Username atau password salah.')   # Tampilkan pesan kesalahan
    return render(request, 'proyek/login.html')   # Tampilkan form login

# ====== RESET PASSWORD (LANGKAH 1 - INPUT EMAIL) ======
def reset_password_email_view(request):
    # Pengguna masukkan email → jika cocok, arahkan ke halaman set password baru
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            return redirect('set_new_password', user_id=user.id)
        except User.DoesNotExist:
            messages.error(request, 'Email tidak ditemukan.')
            return redirect('reset_password_email')
    return render(request, 'proyek/password_reset.html')   # Form input email

# ====== RESET PASSWORD (LANGKAH 2 - SET PASSWORD BARU) ======
def set_new_password_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = CustomSetPasswordForm(user, request.POST or None)   # Form custom reset password

    if request.method == 'POST':
        print("📥 POST diterima")
        if form.is_valid():
            print("✅ Form valid, menyimpan password...")
            form.save()   # Simpan password baru
            messages.success(request, 'Kata sandi berhasil diatur ulang.')
            return redirect('login')
        else:
            print("❌ Form TIDAK valid:", form.errors)

    return render(request, 'proyek/set_new_password.html', {'form': form})

# ====== HALAMAN PROFIL USER ======
def profile_user(request):
    # Menampilkan halaman profil user (saat ini hanya render template)
    return render(request, 'proyek/profile_user.html')

# ====== HOMEPAGE ======
@login_required   # hanya bisa diakses setelah login
def homepage(request):
    semua_proyek = Project.objects.all()   # Ambil semua proyek dari database
    return render(request, 'proyek/homepage.html', {
        'semua_proyek': semua_proyek
    })

# ====== TAMBAH PROYEK ======
def tambah_proyek(request):
    if request.method == 'POST':
        # Cek apakah user klik tombol "Simpan dan Tambah Pekerjaan"
        if 'save_and_add_pekerjaan' in request.POST:
            request.session['draft_proyek'] = request.POST   # Simpan data proyek sementara di session
            return redirect('draft_daftar_pekerjaan')   # Redirect ke form pekerjaan

        form = ProjectForm(request.POST)   # Inisialisasi form proyek
        if form.is_valid():
            proyek = form.save(commit=False)   # Buat instance proyek tanpa langsung simpan
            proyek.save()   # Simpan proyek ke DB

            # Ambil data anggota dari inputan "id:role,id:role"
            anggota_input = request.POST.get('members', '')
            if anggota_input:
                parsed = anggota_input.split(',')
                for item in parsed:
                    if ':' in item:
                        id_str, role = item.split(':', 1)
                        if id_str.strip().isdigit():
                            member_id = int(id_str.strip())
                            # Simpan relasi proyek dengan member dan role-nya
                            ProjectMember.objects.create(
                                project=proyek,
                                member_id=member_id,
                                role=role.strip()
                            )

            return redirect('homepage')   # Setelah berhasil, kembali ke halaman utama
    else:
        # Ambil data draft proyek dari session (jika ada)
        initial_data = request.session.pop('draft_proyek', None)
        form = ProjectForm(initial=initial_data) if initial_data else ProjectForm()

    anggota_list = TeamMember.objects.all()   # Ambil daftar semua anggota
    return render(request, 'proyek/form_proyek.html', {
        'form': form,
        'anggota_list': anggota_list
    })

# ====== EDIT PROYEK ======
def edit_proyek(request, pk):
    proyek = get_object_or_404(Project, pk=pk)
    anggota_list = TeamMember.objects.all()

    # Cegah pengeditan jika proyek sudah ditutup
    if proyek.status == 'Selesai':
        messages.error(request, "Proyek sudah ditutup dan tidak bisa diubah.")
        return redirect('homepage')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=proyek)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.save()

            # Proses anggota baru dari input
            anggota_input = request.POST.get('members', '')
            parsed = anggota_input.split(',') if anggota_input else []
            id_list = []
            role_map = {}

            for item in parsed:
                if ':' in item:
                    id_str, role = item.split(':', 1)
                    if id_str.strip().isdigit():
                        id_int = int(id_str.strip())
                        id_list.append(id_int)
                        role_map[id_int] = role.strip()

            # Hapus member yang tidak ada dalam list baru
            ProjectMember.objects.filter(project=proyek).exclude(member_id__in=id_list).delete()

            # Tambah atau update member baru
            for member_id in id_list:
                role = role_map.get(member_id, "")
                ProjectMember.objects.update_or_create(
                    project=proyek,
                    member_id=member_id,
                    defaults={'role': role}
                )

            return redirect('homepage')
    else:
        form = ProjectForm(instance=proyek)

    # Ambil anggota proyek yang sudah terdaftar sebelumnya
    selected_members = ProjectMember.objects.filter(project=proyek).select_related("member")
    selected_member_dict = {
        str(pm.member.id): pm.role for pm in selected_members
    }

    return render(request, 'proyek/form_proyek.html', {
        'form': form,
        'anggota_list': anggota_list,
        'selected_members': selected_member_dict,
        'proyek': proyek   # digunakan untuk bedakan mode edit/tambah
    })

def hapus_proyek(request, pk):
    proyek = get_object_or_404(Project, pk=pk)
    proyek.delete()   # Hapus proyek dari database
    return redirect('homepage')

# ====== DAFTAR PEKERJAAN DALAM PROYEK TERTENTU ======
def daftar_pekerjaan(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)
    daftar = proyek.pekerjaan.all()   # Ambil semua pekerjaan dari proyek tersebut
    return render(request, 'proyek/daftar_pekerjaan.html', {
        'proyek': proyek,
        'daftar_pekerjaan': daftar
    })

# ====== TAMBAH PEKERJAAN ======
def tambah_pekerjaan(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)
    anggota_list = TeamMember.objects.all()   # Daftar anggota untuk dipilih sebagai pelaksana

    # Cek apakah proyek sudah ditutup
    if proyek.status == 'Selesai':
        messages.error(request, "Proyek sudah ditutup. Tidak bisa menambah pekerjaan.")
        return render(request, 'proyek/form_pekerjaan.html', {
            'form': PekerjaanForm(),
            'proyek': proyek,
            'anggota_list': anggota_list
        })

    if request.method == 'POST':
        form = PekerjaanForm(request.POST)
        if form.is_valid():
            pekerjaan = form.save(commit=False)
            pekerjaan.project = proyek   # Tetapkan proyek

            # Ambil ID pelaksana (dalam bentuk string terpisah koma)
            pelaksana_ids = request.POST.get("pelaksana", "")
            if pelaksana_ids:
                pelaksana_nama = [
                    TeamMember.objects.get(id=int(pid)).name
                    for pid in pelaksana_ids.split(",") if pid.strip().isdigit()
                ]
                pekerjaan.pelaksana = ", ".join(pelaksana_nama)

            pekerjaan.save()
            return redirect('daftar_pekerjaan', proyek_id=proyek.id)
    else:
        form = PekerjaanForm()

    return render(request, 'proyek/form_pekerjaan.html', {
        'form': form,
        'proyek': proyek,
        'anggota_list': anggota_list
    })

# ====== EDIT PEKERJAAN ======
def edit_pekerjaan(request, pk):
    pekerjaan = get_object_or_404(Pekerjaan, pk=pk)
    proyek = pekerjaan.project
    anggota_list = TeamMember.objects.all()

    # Cegah pengeditan jika proyek sudah ditutup
    if proyek.status == 'Selesai':
        messages.error(request, "Tidak bisa mengubah pekerjaan karena proyek sudah ditutup.")
        return redirect('daftar_pekerjaan', proyek_id=proyek.id)

    if request.method == 'POST':
        form = PekerjaanForm(request.POST, instance=pekerjaan)
        if form.is_valid():
            pekerjaan = form.save(commit=False)

            pelaksana_ids = request.POST.get("pelaksana", "")
            if pelaksana_ids.strip():
                pelaksana_nama = [
                    TeamMember.objects.get(id=int(pid)).name
                    for pid in pelaksana_ids.split(",") if pid.strip().isdigit()
                ]
                pekerjaan.pelaksana = ", ".join(pelaksana_nama)
            else:
                pekerjaan.pelaksana = ""

            pekerjaan.save()
            return redirect('daftar_pekerjaan', proyek_id=proyek.id)
        else:
            print("❌ Form error:", form.errors)
    else:
        form = PekerjaanForm(instance=pekerjaan)

    return render(request, 'proyek/form_pekerjaan.html', {
        'form': form,
        'proyek': proyek,
        'anggota_list': anggota_list,
        'pekerjaan': pekerjaan
    })

# ====== HAPUS PEKERJAAN ======
def hapus_pekerjaan(request, pk):
    pekerjaan = get_object_or_404(Pekerjaan, pk=pk)
    proyek = pekerjaan.project

    # Tidak bisa hapus pekerjaan jika proyek sudah selesai
    if proyek.status == 'Selesai':
        messages.error(request, "Tidak bisa menghapus pekerjaan karena proyek sudah ditutup.")
        return redirect('daftar_pekerjaan', proyek_id=proyek.id)

    pekerjaan.delete()
    return redirect('daftar_pekerjaan', proyek_id=proyek.id)

# ====== DETAIL PEKERJAAN (Termasuk Aktivitas) ======
def detail_pekerjaan(request, pekerjaan_id):
    pekerjaan = get_object_or_404(Pekerjaan, id=pekerjaan_id)
    aktivitas = pekerjaan.aktivitas.all()   # Ambil semua aktivitas di dalam pekerjaan
    return render(request, 'proyek/detail_pekerjaan.html', {
        'pekerjaan': pekerjaan,
        'aktivitas': aktivitas
    })

# ====== TAMBAH AKTIVITAS ======
def tambah_aktivitas(request, pekerjaan_id):
    pekerjaan = get_object_or_404(Pekerjaan, id=pekerjaan_id)
    anggota_list = TeamMember.objects.all()

    # Cegah jika proyek sudah ditutup
    if pekerjaan.project.status == 'Selesai':
        messages.error(request, "Proyek sudah ditutup. Tidak bisa menambah aktivitas.")
        return render(request, 'proyek/form_aktivitas.html', {
            'form': AktivitasForm(),
            'pekerjaan': pekerjaan,
            'anggota_list': anggota_list
        })

    if request.method == 'POST':
        form = AktivitasForm(request.POST)
        if form.is_valid():
            aktivitas = form.save(commit=False)
            aktivitas.pekerjaan = pekerjaan

            pelaksana_ids = request.POST.get("pelaksana", "")
            if pelaksana_ids.strip():
                pelaksana_nama = [
                    TeamMember.objects.get(id=int(pid)).name
                    for pid in pelaksana_ids.split(",") if pid.strip().isdigit()
                ]
                aktivitas.pelaksana = ", ".join(pelaksana_nama)
            else:
                aktivitas.pelaksana = ""

            aktivitas.save()
            return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan.id)
    else:
        form = AktivitasForm()

    return render(request, 'proyek/form_aktivitas.html', {
        'form': form,
        'pekerjaan': pekerjaan,
        'anggota_list': anggota_list
    })

# ====== EDIT AKTIVITAS ======
def edit_aktivitas(request, aktivitas_id):
    aktivitas = get_object_or_404(Aktivitas, id=aktivitas_id)
    pekerjaan = aktivitas.pekerjaan
    anggota_list = TeamMember.objects.all()

    # Tidak bisa edit jika proyek sudah selesai
    if pekerjaan.project.status == 'Selesai':
        messages.error(request, "Tidak bisa mengubah aktivitas karena proyek sudah ditutup.")
        return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan.id)

    if request.method == 'POST':
        form = AktivitasForm(request.POST, instance=aktivitas)
        if form.is_valid():
            aktivitas = form.save(commit=False)
            aktivitas.pekerjaan = pekerjaan

            pelaksana_ids = request.POST.get("pelaksana", "")
            if pelaksana_ids.strip():
                pelaksana_nama = [
                    TeamMember.objects.get(id=int(pid)).name
                    for pid in pelaksana_ids.split(",") if pid.strip().isdigit()
                ]
                aktivitas.pelaksana = ", ".join(pelaksana_nama)
            else:
                aktivitas.pelaksana = ""

            aktivitas.save()
            return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan.id)
    else:
        form = AktivitasForm(instance=aktivitas)

    return render(request, 'proyek/form_aktivitas.html', {
        'form': form,
        'pekerjaan': pekerjaan,
        'anggota_list': anggota_list,
        'aktivitas': aktivitas,
    })

# ====== HAPUS AKTIVITAS ======
def hapus_aktivitas(request, aktivitas_id):
    aktivitas = get_object_or_404(Aktivitas, id=aktivitas_id)
    proyek = aktivitas.pekerjaan.project
    pekerjaan_id = aktivitas.pekerjaan.id

    # Cek status proyek
    if proyek.status == 'Selesai':
        messages.error(request, "Tidak bisa menghapus aktivitas karena proyek sudah ditutup.")
        return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan_id)

    aktivitas.delete()
    return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan_id)

# ====== TAMBAH ANGGOTA TIM ======
def tambah_anggota(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST)
        photo_data = request.POST.get('photo_base64', '')

        if form.is_valid():
            anggota = form.save(commit=False)
            # Cek jika ada foto dalam bentuk base64
            if photo_data.startswith('data:image'):
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                anggota.photo = ContentFile(base64.b64decode(imgstr), name=f"photo.{ext}")
            anggota.save()
            return redirect('list_anggota')
    else:
        form = TeamMemberForm()
    return render(request, 'proyek/profil_anggota.html', {'form': form})

# ====== LIST SEMUA ANGGOTA ======
def list_anggota(request):
    query = request.GET.get('q')   # Jika user cari berdasarkan nama
    if query:
        anggota_list = TeamMember.objects.filter(name__icontains=query).order_by('name')
    else:
        anggota_list = TeamMember.objects.all().order_by('name')
    return render(request, 'proyek/profile_team.html', {'anggota_list': anggota_list})

# ====== EDIT ANGGOTA ======
def edit_anggota(request, pk):
    anggota = get_object_or_404(TeamMember, pk=pk)

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=anggota)
        photo_data = request.POST.get('photo_base64', '')

        if form.is_valid():
            anggota = form.save(commit=False)

            # Hapus foto jika kosong
            if photo_data == "":
                if anggota.photo:
                    anggota.photo.delete(save=False)
                anggota.photo = None

            # Atau simpan foto baru jika ada
            elif photo_data.startswith('data:image'):
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                anggota.photo = ContentFile(base64.b64decode(imgstr), name=f"photo.{ext}")

            anggota.save()
            return redirect('list_anggota')
    else:
        form = TeamMemberForm(instance=anggota)

    return render(request, 'proyek/profil_anggota.html', {
        'form': form,
        'anggota': anggota
    })

# ====== HAPUS ANGGOTA ======
def hapus_anggota(request, pk):
    anggota = get_object_or_404(TeamMember, pk=pk)
    anggota.delete()
    return redirect('list_anggota')

# ====== DETAIL ANGGOTA ======
def detail_anggota(request, pk):
    anggota = get_object_or_404(TeamMember, pk=pk)
    return render(request, 'proyek/detail_anggota.html', {'anggota': anggota})

# ====== CETAK PROYEK (PRINT VIEW) ======
def print_proyek(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)
    pelaksana = ProjectMember.objects.filter(project=proyek).select_related("member")
    pekerjaan_list = proyek.pekerjaan.all().prefetch_related("aktivitas")

    return render(request, 'proyek/print_proyek.html', {
        'proyek': proyek,
        'pelaksana': pelaksana,
        'pekerjaan_list': pekerjaan_list
    })

# ====== TUTUP PROYEK ======
@login_required
def tutup_proyek(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)

    if request.method == 'POST':
        form = TutupProyekForm(request.POST, request.FILES, instance=proyek)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.status = 'Selesai'   # Tandai proyek sudah ditutup
            proyek.save()
            messages.success(request, "Proyek berhasil ditutup.")
            return redirect('homepage')
        else:
            messages.error(request, "Terjadi kesalahan. Pastikan semua data diisi.")
    else:
        form = TutupProyekForm(instance=proyek)

    return render(request, 'proyek/tutup_proyek.html', {'form': form, 'proyek': proyek})

# ====== GRAFIK PROGRES PROYEK PER TAHUN ======
def progres_proyek(request):
    selected_year = int(request.GET.get("year", datetime.now().year))
    start_of_year = date(selected_year, 1, 1)
    end_of_year = date(selected_year, 12, 31)

    # Ambil proyek yang aktif (sebagian atau penuh) pada tahun tersebut
    semua_proyek = Project.objects.filter(
        start_date__lte=end_of_year,
        end_date__gte=start_of_year
    )

    proyek_data = []
    for proyek in semua_proyek:
        proyek_data.append({
            "nama": proyek.name,
            "mulai": proyek.start_date.strftime('%Y-%m-%d'),
            "selesai": proyek.end_date.strftime('%Y-%m-%d'),
            "status": proyek.status
        })

    # Ambil range tahun dari semua proyek
    all_years = Project.objects.aggregate(
        min_year=Min("start_date"),
        max_year=Max("end_date")
    )

    if all_years["min_year"] and all_years["max_year"]:
        years = list(range(all_years["min_year"].year, all_years["max_year"].year + 1))
    else:
        years = [selected_year]

    context = {
        "data_proyek_json": json.dumps(proyek_data, cls=DjangoJSONEncoder),
        "selected_year": selected_year,
        "years": years,
    }

    return render(request, 'proyek/view_progress.html', context)

# ====== HALAMAN INTEGRASI ANTAR APLIKASI ======
@login_required
def integrasi_aplikasi(request):
    projects = Project.objects.all()
    return render(request, 'proyek/integrasi.html', {'projects': projects})

# ====== API ENDPOINT UNTUK MELIHAT PROYEK (READONLY) ======
class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    # Izinkan siapa saja untuk mengakses API ini (untuk pengembangan)
    permission_classes = [permissions.AllowAny] # <--- TAMBAHAN: Untuk izin akses API

    @action(detail=False, methods=['get'], url_path='status-only')
    def status_only(self, request):
        projects = Project.objects.all()
        serializer = ProjectStatusOnlySerializer(projects, many=True)
        return Response(serializer.data)

# ====== ALTERNATIF API BERDASARKAN APIView (non-ViewSet) ======
# BARIS INI DIHAPUS UNTUK MENGHINDARI DUPLIKASI ENDPOINT STATUS-ONLY
# class ProjectStatusOnlyAPIView(APIView):
#    def get(self. request):
#        projects = Project.objects.all()
#        serializer = ProjectStatusOnlySerializer(projects, many=True)
#        return Response(serializer.data)