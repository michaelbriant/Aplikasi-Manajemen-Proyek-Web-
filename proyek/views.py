# proyek/views.py

# ====== IMPORT DARI DJANGO & LIB TAMBAHAN ======
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

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
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Min, Max

from datetime import datetime, date
import base64
import json
import requests # <--- PASTIKAN INI ADA, SUDAH ADA DI KODE ANDA

# ====== REST FRAMEWORK UNTUK API VIEW & ENDPOINT ======
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions

# ====== LANDING PAGE ======
def landing_page(request):
    # Menampilkan halaman landing.html (beranda publik sebelum login)
    return render(request, 'proyek/landing.html')

# ====== LOGOUT ======
def custom_logout(request):
    # Fungsi logout untuk mengakhiri sesi pengguna
    logout(request)
    return redirect('landing')

# ====== REGISTRASI ======
def register(request):
    # Registrasi akun baru menggunakan form kustom
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'proyek/register.html', {'form': form})

# ====== LOGIN VIEW ======
def login_view(request):
    # Fungsi login: menerima username & password lalu login
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Username atau password salah.')
    return render(request, 'proyek/login.html')

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
    return render(request, 'proyek/password_reset.html')

# ====== RESET PASSWORD (LANGKAH 2 - SET PASSWORD BARU) ======
def set_new_password_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = CustomSetPasswordForm(user, request.POST or None)

    if request.method == 'POST':
        print("📥 POST diterima")
        if form.is_valid():
            print("✅ Form valid, menyimpan password...")
            form.save()
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
@login_required
def homepage(request):
    semua_proyek = Project.objects.all()
    return render(request, 'proyek/homepage.html', {
        'semua_proyek': semua_proyek
    })

# ====== TAMBAH PROYEK ======
def tambah_proyek(request):
    if request.method == 'POST':
        if 'save_and_add_pekerjaan' in request.POST:
            request.session['draft_proyek'] = request.POST
            return redirect('draft_daftar_pekerjaan')

        form = ProjectForm(request.POST)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.save()

            anggota_input = request.POST.get('members', '')
            if anggota_input:
                parsed = anggota_input.split(',')
                for item in parsed:
                    if ':' in item:
                        id_str, role = item.split(':', 1)
                        if id_str.strip().isdigit():
                            member_id = int(id_str.strip())
                            ProjectMember.objects.create(
                                project=proyek,
                                member_id=member_id,
                                role=role.strip()
                            )
            return redirect('homepage')
    else:
        initial_data = request.session.pop('draft_proyek', None)
        form = ProjectForm(initial=initial_data) if initial_data else ProjectForm()

    anggota_list = TeamMember.objects.all()
    return render(request, 'proyek/form_proyek.html', {
        'form': form,
        'anggota_list': anggota_list
    })

# ====== EDIT PROYEK ======
def edit_proyek(request, pk):
    proyek = get_object_or_404(Project, pk=pk)
    anggota_list = TeamMember.objects.all()

    if proyek.status == 'Selesai':
        messages.error(request, "Proyek sudah ditutup dan tidak bisa diubah.")
        return redirect('homepage')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=proyek)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.save()

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

            ProjectMember.objects.filter(project=proyek).exclude(member_id__in=id_list).delete()

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

    selected_members = ProjectMember.objects.filter(project=proyek).select_related("member")
    selected_member_dict = {
        str(pm.member.id): pm.role for pm in selected_members
    }

    return render(request, 'proyek/form_proyek.html', {
        'form': form,
        'anggota_list': anggota_list,
        'selected_members': selected_member_dict,
        'proyek': proyek
    })

def hapus_proyek(request, pk):
    proyek = get_object_or_404(Project, pk=pk)
    proyek.delete()
    return redirect('homepage')

# ====== DAFTAR PEKERJAAN DALAM PROYEK TERTENTU ======
def daftar_pekerjaan(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)
    daftar = proyek.pekerjaan.all()
    return render(request, 'proyek/daftar_pekerjaan.html', {
        'proyek': proyek,
        'daftar_pekerjaan': daftar
    })

# ====== TAMBAH PEKERJAAN ======
def tambah_pekerjaan(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)
    anggota_list = TeamMember.objects.all()

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
            pekerjaan.project = proyek

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
                pekerjaan.pelaksana = ", ".join(pelaksana_nama) # BUGFIX applied: pekerjaan.pelaksana
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

    if proyek.status == 'Selesai':
        messages.error(request, "Tidak bisa menghapus pekerjaan karena proyek sudah ditutup.")
        return redirect('daftar_pekerjaan', proyek_id=proyek.id)

    pekerjaan.delete()
    return redirect('daftar_pekerjaan', proyek_id=proyek.id)

# ====== DETAIL PEKERJAAN (Termasuk Aktivitas) ======
def detail_pekerjaan(request, pekerjaan_id):
    pekerjaan = get_object_or_404(Pekerjaan, id=pekerjaan_id)
    aktivitas = pekerjaan.aktivitas.all()
    return render(request, 'proyek/detail_pekerjaan.html', {
        'pekerjaan': pekerjaan,
        'aktivitas': aktivitas
    })

# ====== TAMBAH AKTIVITAS ======
def tambah_aktivitas(request, pekerjaan_id):
    pekerjaan = get_object_or_404(Pekerjaan, id=pekerjaan_id)
    anggota_list = TeamMember.objects.all()

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
    query = request.GET.get('q')
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
            if photo_data == "":
                if anggota.photo:
                    anggota.photo.delete(save=False)
                anggota.photo = None
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

    # --- START NEW LOGIC FOR FETCHING EXTERNAL DATA ---
    external_data = {
        'ie': None,
        'ic': None,
        'imp_status': None,
        'imp_detail': None,
    }

    # API Endpoints (copy from integrasi.html JS)
    api_endpoints = {
        'ie': {
            'status': "https://fabyaanusakti.pythonanywhere.com/api/status-only/",
            'detail': "https://fabyaanusakti.pythonanywhere.com/api/projek-data/"
        },
        'ic': {
            'main': "https://arlellll.pythonanywhere.com/api-content/project-statuses/"
        },
        'imp': {
            'status': "https://tasana.pythonanywhere.com/api/project-status/",
            'detail': "https://tasana.pythonanywhere.com/api/projects-nested/"
        }
    }

    # --- Utility functions for formatting (if needed for direct use in Python) ---
    def format_iso_date_py(iso_string):
        if not iso_string:
            return 'N/A'
        try:
            from datetime import datetime
            dt_obj = datetime.fromisoformat(iso_string.replace('Z', '+00:00')) # Handle 'Z' for UTC
            return dt_obj.strftime('%d %B %Y') # e.g., 27 Juni 2025
        except ValueError:
            # Try YYYY-MM-DD format if ISO fails
            if isinstance(iso_string, str) and iso_string.strip().count('-') == 2:
                try:
                    year, month, day = map(int, iso_string.split('-'))
                    dt_obj = datetime(year, month, day)
                    return dt_obj.strftime('%d %B %Y')
                except ValueError:
                    pass # Fall through to return original string
            pass # Fall through to return original string
        return iso_string # Return original string if parsing fails


    try:
        # Fetch data for IE module
        ie_status_res = requests.get(api_endpoints['ie']['status'])
        ie_status_res.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        ie_detail_res = requests.get(api_endpoints['ie']['detail'])
        ie_detail_res.raise_for_status()

        ie_status_list = ie_status_res.json()
        ie_projek_list = ie_detail_res.json()

        # Mencari proyek berdasarkan ID aplikasi Anda (proyek.id)
        external_data['ie'] = {
            'status': next((p for p in ie_status_list if p.get('id') == proyek.id), None),
            'detail': next((p for p in ie_projek_list if p.get('id_projek') == proyek.id), None),
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IE data for printing: {e}")
        messages.warning(request, f"Gagal mengambil data IE untuk cetak: {e}") # Opsional, jika ingin memberitahu user di browser
    except json.JSONDecodeError as e:
        print(f"Error decoding IE JSON for printing: {e}")
        messages.warning(request, f"Gagal membaca format data IE untuk cetak: {e}")


    try:
        # Fetch data for IC module
        ic_main_res = requests.get(api_endpoints['ic']['main'])
        ic_main_res.raise_for_status()

        ic_project_data_list = ic_main_res.json()
        # Mencari proyek berdasarkan external_id (sesuai API IC)
        external_data['ic'] = next((p for p in ic_project_data_list if str(p.get('external_id')) == str(proyek.id)), None)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IC data for printing: {e}")
        messages.warning(request, f"Gagal mengambil data IC untuk cetak: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding IC JSON for printing: {e}")
        messages.warning(request, f"Gagal membaca format data IC untuk cetak: {e}")


    try:
        # Fetch data for IMP module
        imp_status_res = requests.get(api_endpoints['imp']['status'])
        imp_status_res.raise_for_status()
        imp_detail_res = requests.get(api_endpoints['imp']['detail'])
        imp_detail_res.raise_for_status()

        imp_statuses = imp_status_res.json()
        imp_details = imp_detail_res.json()

        # Mencari proyek berdasarkan external_id (sesuai API IMP)
        external_data['imp_status'] = next((p for p in imp_statuses if str(p.get('external_id')) == str(proyek.id)), None)
        external_data['imp_detail'] = next((p for p in imp_details if str(p.get('external_id')) == str(proyek.id)), None)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IMP data for printing: {e}")
        messages.warning(request, f"Gagal mengambil data IMP untuk cetak: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding IMP JSON for printing: {e}")
        messages.warning(request, f"Gagal membaca format data IMP untuk cetak: {e}")


    # --- END NEW LOGIC FOR FETCHING EXTERNAL DATA ---

    # Kirim semua data ke template print_proyek.html
    return render(request, 'proyek/print_proyek.html', {
        'proyek': proyek,           # Data proyek utama dari database Anda
        'pelaksana': pelaksana,     # Anggota pelaksana proyek
        'pekerjaan_list': pekerjaan_list, # Daftar pekerjaan dan aktivitas terkait
        'external_data': external_data, # Data yang diambil dari API eksternal
    })

# ====== TUTUP PROYEK ======
@login_required
def tutup_proyek(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)

    if request.method == 'POST':
        form = TutupProyekForm(request.POST, request.FILES, instance=proyek)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.status = 'Selesai'
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

# ====== API ENDPOINT UNTUK MANAJEMEN PROYEK (LENGKAP) ======
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], url_path='status-only')
    def status_only(self, request):
        projects = Project.objects.all()
        serializer = ProjectStatusOnlySerializer(projects, many=True)
        return Response(serializer.data)