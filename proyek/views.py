from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Project, TeamMember, ProjectMember, Pekerjaan, Aktivitas, PenutupanProyek
from .forms import ProjectForm, TeamMemberForm, PekerjaanForm, AktivitasForm
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import datetime
from django.db.models import Q
from django.db.models import Min, Max
from datetime import date
import base64
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from .serializers import ProjectSerializer
import requests
from django.contrib.auth.forms import SetPasswordForm
from .forms import CustomUserCreationForm
from .forms import TutupProyekForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project
from .models import Project, IntegrasiPesan
from django.views.decorators.csrf import csrf_exempt
import requests
from .forms import CustomSetPasswordForm 
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectStatusOnlySerializer
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response



# ------------------- landing page & login -------------------
def landing_page(request):
    return render(request, 'proyek/landing.html')

def custom_logout(request):
    logout(request)
    return redirect('landing')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'proyek/register.html', {'form': form})

def login_view(request):
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

def reset_password_email_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            return redirect('set_new_password', user_id=user.id)
        except User.DoesNotExist:
            messages.error(request, 'Email tidak ditemukan.')
            return redirect('reset_password_email')
    return render(request, 'proyek/password_reset.html')

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

# ------------------- profile -------------------
def profile_user(request):
    return render(request, 'proyek/profile_user.html')

# ------------------- HOMEPAGE -------------------
@login_required
def homepage(request):
    semua_proyek = Project.objects.all()
    return render(request, 'proyek/homepage.html', {'semua_proyek': semua_proyek})

# ------------------- TAMBAH PROYEK -------------------
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

            # Ini tetap dijalankan meskipun `id_list` kosong!
            ProjectMember.objects.filter(project=proyek).exclude(member_id__in=id_list).delete()

            # Tambahkan atau update yang baru
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

    # Inisialisasi anggota proyek yang terpilih (id dan role)
    selected_members = ProjectMember.objects.filter(project=proyek).select_related("member")
    selected_member_dict = {
        str(pm.member.id): pm.role for pm in selected_members
    }

    return render(request, 'proyek/form_proyek.html', {
        'form': form,
        'anggota_list': anggota_list,
        'selected_members': selected_member_dict,
        'proyek': proyek  # ← untuk membedakan mode edit
    })

def hapus_proyek(request, pk):
    proyek = get_object_or_404(Project, pk=pk)
    proyek.delete()
    return redirect('homepage')

def daftar_pekerjaan(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)
    daftar = proyek.pekerjaan.all()
    return render(request, 'proyek/daftar_pekerjaan.html', {'proyek': proyek, 'daftar_pekerjaan': daftar})

def tambah_pekerjaan(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)
    anggota_list = TeamMember.objects.all()  

    if proyek.status == 'Selesai':
        messages.error(request, "Proyek sudah ditutup. Tidak bisa menambah pekerjaan.")
        return render(request, 'proyek/form_pekerjaan.html', {
            'form': PekerjaanForm(),
            'proyek': proyek,
            'anggota_list': TeamMember.objects.all()
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

def edit_pekerjaan(request, pk):
    pekerjaan = get_object_or_404(Pekerjaan, pk=pk)
    proyek = pekerjaan.project
    anggota_list = TeamMember.objects.all()

    if pekerjaan.project.status == 'Selesai':
        messages.error(request, "Tidak bisa mengubah pekerjaan karena proyek sudah ditutup.")
        return redirect('daftar_pekerjaan', proyek_id=proyek.id)

    if request.method == 'POST':
        form = PekerjaanForm(request.POST, instance=pekerjaan)
        if form.is_valid():
            pekerjaan = form.save(commit=False)
            pekerjaan.project = proyek

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

def hapus_pekerjaan(request, pk):
    pekerjaan = get_object_or_404(Pekerjaan, pk=pk)
    proyek = pekerjaan.project

    if proyek.status == 'Selesai':
        messages.error(request, "Tidak bisa menghapus pekerjaan karena proyek sudah ditutup.")
        return redirect('daftar_pekerjaan', proyek_id=proyek.id)

    pekerjaan.delete()
    return redirect('daftar_pekerjaan', proyek_id=proyek.id)

def detail_pekerjaan(request, pekerjaan_id):
    pekerjaan = get_object_or_404(Pekerjaan, id=pekerjaan_id)
    aktivitas = pekerjaan.aktivitas.all()    
    return render(request, 'proyek/detail_pekerjaan.html', {'pekerjaan': pekerjaan, 'aktivitas': aktivitas})

def tambah_aktivitas(request, pekerjaan_id):
    pekerjaan = get_object_or_404(Pekerjaan, id=pekerjaan_id)
    anggota_list = TeamMember.objects.all()

    if pekerjaan.project.status == 'Selesai':
        messages.error(request, "Proyek sudah ditutup. Tidak bisa menambah aktivitas.")
        return render(request, 'proyek/form_aktivitas.html', {
            'form': AktivitasForm(),
            'pekerjaan': pekerjaan,
            'anggota_list': TeamMember.objects.all()
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

def edit_aktivitas(request, aktivitas_id):
    aktivitas = get_object_or_404(Aktivitas, id=aktivitas_id)
    pekerjaan = aktivitas.pekerjaan
    anggota_list = TeamMember.objects.all()

    if aktivitas.pekerjaan.project.status == 'Selesai':
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

def hapus_aktivitas(request, aktivitas_id):
    aktivitas = get_object_or_404(Aktivitas, id=aktivitas_id)
    proyek = aktivitas.pekerjaan.project
    pekerjaan_id = aktivitas.pekerjaan.id

    if proyek.status == 'Selesai':
        messages.error(request, "Tidak bisa menghapus aktivitas karena proyek sudah ditutup.")
        return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan_id)

    aktivitas.delete()
    return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan_id)

# ------------------- ANGGOTA -------------------
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

def list_anggota(request):
    query = request.GET.get('q')
    if query:
        anggota_list = TeamMember.objects.filter(name__icontains=query).order_by('name')
    else:
        anggota_list = TeamMember.objects.all().order_by('name')
    return render(request, 'proyek/profile_team.html', {'anggota_list': anggota_list})

def edit_anggota(request, pk):
    anggota = get_object_or_404(TeamMember, pk=pk)

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=anggota)
        photo_data = request.POST.get('photo_base64', '')

        if form.is_valid():
            anggota = form.save(commit=False)

            # 1. Jika pengguna hapus foto (photo_base64 kosong)
            if photo_data == "":
                if anggota.photo:
                    anggota.photo.delete(save=False)
                anggota.photo = None

            # 2. Jika pengguna unggah atau ambil foto baru (base64)
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

def hapus_anggota(request, pk):
    anggota = get_object_or_404(TeamMember, pk=pk)
    anggota.delete()
    return redirect('list_anggota')

def detail_anggota(request, pk):
    anggota = get_object_or_404(TeamMember, pk=pk)
    return render(request, 'proyek/detail_anggota.html', {'anggota': anggota})

# ------------------- HAPUS PROYEK -------------------
def hapus_proyek(request, pk):
    proyek = get_object_or_404(Project, pk=pk)
    proyek.delete()
    return redirect('homepage')

def print_proyek(request, proyek_id):
    proyek = get_object_or_404(Project, id=proyek_id)
    pelaksana = ProjectMember.objects.filter(project=proyek).select_related("member")
    pekerjaan_list = proyek.pekerjaan.all().prefetch_related("aktivitas")

    return render(request, 'proyek/print_proyek.html', {
        'proyek': proyek,
        'pelaksana': pelaksana,
        'pekerjaan_list': pekerjaan_list
    })

def progres_proyek(request):
    selected_year = int(request.GET.get("year", datetime.now().year))
    start_of_year = date(selected_year, 1, 1)
    end_of_year = date(selected_year, 12, 31)

    # Ambil proyek yang aktif sebagian atau seluruhnya di tahun yang dipilih
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

    # Ambil tahun awal dan akhir dari semua proyek
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

class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(detail=False, methods=['get'], url_path='status-only')
    def status_only(self, request):
        projects = Project.objects.all()
        serializer = ProjectStatusOnlySerializer(projects, many=True)
        return Response(serializer.data)

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

@login_required
def integrasi_aplikasi(request):
    projects = Project.objects.all()
    return render(request, 'proyek/integrasi.html', {'projects': projects})

class ProjectStatusOnlyAPIView(APIView):
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectStatusOnlySerializer(projects, many=True)
        return Response(serializer.data)
