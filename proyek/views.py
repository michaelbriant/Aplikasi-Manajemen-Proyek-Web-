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
    """
    Menampilkan halaman landing (beranda publik sebelum pengguna login).
    Template yang digunakan: 'proyek/landing.html'.
    """
    return render(request, 'proyek/landing.html')

# ====== LOGOUT ======
def custom_logout(request):
    """
    Fungsi ini menangani proses logout pengguna.
    Mengakhiri sesi pengguna saat ini dan mengarahkan ke halaman landing.
    """
    logout(request)
    return redirect('landing')

# ====== REGISTRASI ======
def register(request):
    """
    Menangani proses registrasi akun pengguna baru.
    Jika metode permintaan adalah POST dan form valid, pengguna baru akan disimpan
    dan diarahkan ke halaman login. Jika tidak, form registrasi akan ditampilkan.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun berhasil dibuat! Silakan login.')
            return redirect('login')
        else:
            messages.error(request, 'Terjadi kesalahan saat pendaftaran. Mohon periksa kembali input Anda.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'proyek/register.html', {'form': form})

# ====== LOGIN VIEW ======
def login_view(request):
    """
    Menangani proses login pengguna.
    Jika metode permintaan adalah POST, akan memverifikasi username dan password.
    Jika kredensial benar, pengguna akan di-login dan diarahkan ke homepage.
    Jika salah, pesan error akan ditampilkan.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Selamat datang, {user.username}!')
            return redirect('homepage')
        else:
            messages.error(request, 'Username atau password salah.')
    return render(request, 'proyek/login.html')

# ====== RESET PASSWORD (LANGKAH 1 - INPUT EMAIL) ======
def reset_password_email_view(request):
    """
    Langkah pertama dalam proses reset kata sandi.
    Pengguna diminta memasukkan email mereka. Jika email ditemukan,
    akan diarahkan ke halaman untuk mengatur kata sandi baru.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Mengarahkan pengguna ke halaman set password baru dengan ID pengguna
            return redirect('set_new_password', user_id=user.id)
        except User.DoesNotExist:
            messages.error(request, 'Email tidak ditemukan.')
            return redirect('reset_password_email')
    return render(request, 'proyek/password_reset.html')

# ====== RESET PASSWORD (LANGKAH 2 - SET PASSWORD BARU) ======
def set_new_password_view(request, user_id):
    """
    Langkah kedua dalam proses reset kata sandi.
    Pengguna dapat mengatur kata sandi baru untuk akun mereka.
    Mengambil objek User berdasarkan user_id. Jika form valid, kata sandi diperbarui.
    """
    user = get_object_or_404(User, id=user_id)
    # Inisialisasi form dengan instance pengguna
    form = CustomSetPasswordForm(user, request.POST or None)

    if request.method == 'POST':
        print("📥 POST diterima") # Debugging: Menunjukkan permintaan POST diterima
        if form.is_valid():
            print("✅ Form valid, menyimpan password...") # Debugging: Menunjukkan form valid
            form.save()
            messages.success(request, 'Kata sandi berhasil diatur ulang.')
            return redirect('login')
        else:
            print("❌ Form TIDAK valid:", form.errors) # Debugging: Menunjukkan error form jika tidak valid
            messages.error(request, 'Terjadi kesalahan saat mengatur ulang kata sandi. Mohon periksa kembali.')

    return render(request, 'proyek/set_new_password.html', {'form': form})

# ====== HALAMAN PROFIL USER ======
def profile_user(request):
    """
    Menampilkan halaman profil pengguna.
    Saat ini hanya merender template statis 'proyek/profile_user.html'.
    """
    return render(request, 'proyek/profile_user.html')

# ====== HOMEPAGE ======
@login_required
def homepage(request):
    """
    Menampilkan halaman beranda setelah login, berisi daftar semua proyek.
    Membutuhkan pengguna untuk login (menggunakan decorator @login_required).
    """
    semua_proyek = Project.objects.all()
    return render(request, 'proyek/homepage.html', {
        'semua_proyek': semua_proyek
    })

# ====== TAMBAH PROYEK ======
def tambah_proyek(request):
    """
    Menangani penambahan proyek baru.
    Jika permintaan POST, form akan divalidasi.
    Ada opsi 'save_and_add_pekerjaan' yang akan menyimpan data proyek sementara di sesi
    dan mengarahkan ke halaman penambahan pekerjaan.
    Jika tidak, proyek akan disimpan dan anggota tim terkait akan ditambahkan.
    """
    if request.method == 'POST':
        if 'save_and_add_pekerjaan' in request.POST:
            # Simpan data form proyek sebagai draft di sesi
            request.session['draft_proyek'] = request.POST
            return redirect('draft_daftar_pekerjaan') # Arahkan ke halaman draft pekerjaan

        form = ProjectForm(request.POST)
        if form.is_valid():
            proyek = form.save(commit=False) # Simpan form tanpa langsung commit ke DB
            proyek.save() # Simpan instance proyek

            # Tangani penambahan anggota proyek dari input form
            anggota_input = request.POST.get('members', '')
            if anggota_input:
                # Memparsing string anggota (misal: "1:Manajer, 2:Staf")
                parsed = anggota_input.split(',')
                for item in parsed:
                    if ':' in item:
                        id_str, role = item.split(':', 1)
                        if id_str.strip().isdigit():
                            member_id = int(id_str.strip())
                            # Buat entri ProjectMember untuk proyek ini
                            ProjectMember.objects.create(
                                project=proyek,
                                member_id=member_id,
                                role=role.strip()
                            )
            messages.success(request, 'Proyek berhasil ditambahkan!')
            return redirect('homepage')
        else:
            messages.error(request, 'Terjadi kesalahan saat menambahkan proyek. Mohon periksa kembali input Anda.')
    else:
        # Jika metode GET, coba ambil data draft proyek dari sesi jika ada
        initial_data = request.session.pop('draft_proyek', None)
        form = ProjectForm(initial=initial_data) if initial_data else ProjectForm()

    # Ambil daftar semua anggota tim untuk ditampilkan di form
    anggota_list = TeamMember.objects.all()
    return render(request, 'proyek/form_proyek.html', {
        'form': form,
        'anggota_list': anggota_list
    })

# ====== EDIT PROYEK ======
def edit_proyek(request, pk):
    """
    Menangani pengeditan proyek yang sudah ada.
    Mencegah pengeditan jika status proyek sudah 'Selesai'.
    Memperbarui detail proyek dan mengelola anggota tim proyek (menambah, menghapus, memperbarui peran).
    """
    proyek = get_object_or_404(Project, pk=pk)
    anggota_list = TeamMember.objects.all()

    # Cegah pengeditan jika proyek sudah selesai
    if proyek.status == 'Selesai':
        messages.error(request, "Proyek sudah ditutup dan tidak bisa diubah.")
        return redirect('homepage')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=proyek)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.save()

            # Tangani pembaruan anggota proyek
            anggota_input = request.POST.get('members', '')
            parsed = anggota_input.split(',') if anggota_input else []
            id_list = [] # List ID anggota yang baru
            role_map = {} # Map ID anggota ke perannya

            for item in parsed:
                if ':' in item:
                    id_str, role = item.split(':', 1)
                    if id_str.strip().isdigit():
                        id_int = int(id_str.strip())
                        id_list.append(id_int)
                        role_map[id_int] = role.strip()

            # Hapus anggota yang tidak lagi dipilih
            ProjectMember.objects.filter(project=proyek).exclude(member_id__in=id_list).delete()

            # Tambahkan atau perbarui anggota yang dipilih
            for member_id in id_list:
                role = role_map.get(member_id, "")
                ProjectMember.objects.update_or_create(
                    project=proyek,
                    member_id=member_id,
                    defaults={'role': role} # Perbarui peran jika sudah ada
                )
            messages.success(request, 'Proyek berhasil diperbarui!')
            return redirect('homepage')
        else:
            messages.error(request, 'Terjadi kesalahan saat memperbarui proyek. Mohon periksa kembali input Anda.')
    else:
        form = ProjectForm(instance=proyek)

    # Ambil anggota yang sudah dipilih untuk ditampilkan di form
    selected_members = ProjectMember.objects.filter(project=proyek).select_related("member")
    selected_member_dict = {
        str(pm.member.id): pm.role for pm in selected_members
    }

    return render(request, 'proyek/form_proyek.html', {
        'form': form,
        'anggota_list': anggota_list,
        'selected_members': selected_member_dict,
        'proyek': proyek # Kirim objek proyek untuk keperluan lain di template (misal: tombol hapus)
    })

def hapus_proyek(request, pk):
    """
    Menghapus proyek yang sudah ada berdasarkan primary key (pk).
    Setelah penghapusan, pengguna akan diarahkan kembali ke homepage.
    """
    proyek = get_object_or_404(Project, pk=pk)
    proyek.delete()
    messages.success(request, 'Proyek berhasil dihapus.')
    return redirect('homepage')

# ====== DAFTAR PEKERJAAN DALAM PROYEK TERTENTU ======
def daftar_pekerjaan(request, proyek_id):
    """
    Menampilkan daftar semua pekerjaan yang terkait dengan proyek tertentu.
    Mengambil objek Project berdasarkan proyek_id dan semua Pekerjaan terkait.
    """
    proyek = get_object_or_404(Project, id=proyek_id)
    daftar = proyek.pekerjaan.all() # Mengambil semua pekerjaan dari proyek ini
    return render(request, 'proyek/daftar_pekerjaan.html', {
        'proyek': proyek,
        'daftar_pekerjaan': daftar
    })

# ====== TAMBAH PEKERJAAN ======
def tambah_pekerjaan(request, proyek_id):
    """
    Menambahkan pekerjaan baru ke proyek yang spesifik.
    Mencegah penambahan jika proyek sudah 'Selesai'.
    Memproses PekerjaanForm, mengaitkan pekerjaan dengan proyek, dan menyimpan pelaksana.
    """
    proyek = get_object_or_404(Project, id=proyek_id)
    anggota_list = TeamMember.objects.all()

    # Cegah penambahan pekerjaan jika proyek sudah selesai
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
            pekerjaan.project = proyek # Kaitkan pekerjaan dengan proyek
            
            # Mengelola pelaksana pekerjaan dari input
            pelaksana_ids = request.POST.get("pelaksana", "")
            if pelaksana_ids:
                # Mengambil nama anggota berdasarkan ID yang dipilih
                pelaksana_nama = [
                    TeamMember.objects.get(id=int(pid)).name
                    for pid in pelaksana_ids.split(",") if pid.strip().isdigit()
                ]
                pekerjaan.pelaksana = ", ".join(pelaksana_nama) # Simpan nama pelaksana dalam string
            else:
                pekerjaan.pelaksana = "" # Pastikan kosong jika tidak ada pelaksana

            pekerjaan.save()
            messages.success(request, 'Pekerjaan berhasil ditambahkan.')
            return redirect('daftar_pekerjaan', proyek_id=proyek.id)
        else:
            messages.error(request, 'Terjadi kesalahan saat menambahkan pekerjaan. Mohon periksa kembali input Anda.')
    else:
        form = PekerjaanForm()

    return render(request, 'proyek/form_pekerjaan.html', {
        'form': form,
        'proyek': proyek,
        'anggota_list': anggota_list
    })

# ====== EDIT PEKERJAAN ======
def edit_pekerjaan(request, pk):
    """
    Mengedit pekerjaan yang sudah ada berdasarkan primary key (pk).
    Mencegah pengeditan jika proyek induk sudah 'Selesai'.
    Memperbarui detail pekerjaan, termasuk pelaksana.
    """
    pekerjaan = get_object_or_404(Pekerjaan, pk=pk)
    proyek = pekerjaan.project
    anggota_list = TeamMember.objects.all()

    # Cegah pengeditan jika proyek sudah selesai
    if proyek.status == 'Selesai':
        messages.error(request, "Tidak bisa mengubah pekerjaan karena proyek sudah ditutup.")
        return redirect('daftar_pekerjaan', proyek_id=proyek.id)

    if request.method == 'POST':
        form = PekerjaanForm(request.POST, instance=pekerjaan)
        if form.is_valid():
            pekerjaan = form.save(commit=False)

            # Mengelola pelaksana pekerjaan dari input (mirip dengan tambah_pekerjaan)
            pelaksana_ids = request.POST.get("pelaksana", "")
            if pelaksana_ids.strip():
                pelaksana_nama = [
                    TeamMember.objects.get(id=int(pid)).name
                    for pid in pelaksana_ids.split(",") if pid.strip().isdigit()
                ]
                pekerjaan.pelaksana = ", ".join(pelaksana_nama)
            else:
                pekerjaan.pelaksana = "" # Set kosong jika tidak ada pelaksana yang dipilih

            pekerjaan.save()
            messages.success(request, 'Pekerjaan berhasil diperbarui.')
            return redirect('daftar_pekerjaan', proyek_id=proyek.id)
        else:
            print("❌ Form error:", form.errors) # Debugging: Menampilkan error form
            messages.error(request, 'Terjadi kesalahan saat memperbarui pekerjaan. Mohon periksa kembali input Anda.')
    else:
        form = PekerjaanForm(instance=pekerjaan)

    return render(request, 'proyek/form_pekerjaan.html', {
        'form': form,
        'proyek': proyek,
        'anggota_list': anggota_list,
        'pekerjaan': pekerjaan # Kirim objek pekerjaan untuk keperluan lain di template
    })

# ====== HAPUS PEKERJAAN ======
def hapus_pekerjaan(request, pk):
    """
    Menghapus pekerjaan berdasarkan primary key (pk).
    Mencegah penghapusan jika proyek induk sudah 'Selesai'.
    Setelah penghapusan, akan diarahkan kembali ke daftar pekerjaan proyek tersebut.
    """
    pekerjaan = get_object_or_404(Pekerjaan, pk=pk)
    proyek = pekerjaan.project

    # Cegah penghapusan jika proyek sudah selesai
    if proyek.status == 'Selesai':
        messages.error(request, "Tidak bisa menghapus pekerjaan karena proyek sudah ditutup.")
        return redirect('daftar_pekerjaan', proyek_id=proyek.id)

    pekerjaan.delete()
    messages.success(request, 'Pekerjaan berhasil dihapus.')
    return redirect('daftar_pekerjaan', proyek_id=proyek.id)

# ====== DETAIL PEKERJAAN (Termasuk Aktivitas) ======
def detail_pekerjaan(request, pekerjaan_id):
    """
    Menampilkan detail pekerjaan tertentu, termasuk semua aktivitas yang terkait dengan pekerjaan tersebut.
    """
    pekerjaan = get_object_or_404(Pekerjaan, id=pekerjaan_id)
    aktivitas = pekerjaan.aktivitas.all() # Mengambil semua aktivitas dari pekerjaan ini
    return render(request, 'proyek/detail_pekerjaan.html', {
        'pekerjaan': pekerjaan,
        'aktivitas': aktivitas
    })

# ====== TAMBAH AKTIVITAS ======
def tambah_aktivitas(request, pekerjaan_id):
    """
    Menambahkan aktivitas baru ke pekerjaan yang spesifik.
    Mencegah penambahan jika proyek induk pekerjaan sudah 'Selesai'.
    Memproses AktivitasForm, mengaitkan aktivitas dengan pekerjaan, dan menyimpan pelaksana.
    """
    pekerjaan = get_object_or_404(Pekerjaan, id=pekerjaan_id)
    anggota_list = TeamMember.objects.all()

    # Cegah penambahan aktivitas jika proyek induk sudah selesai
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
            aktivitas.pekerjaan = pekerjaan # Kaitkan aktivitas dengan pekerjaan
            
            # Mengelola pelaksana aktivitas dari input
            pelaksana_ids = request.POST.get("pelaksana", "")
            if pelaksana_ids.strip():
                pelaksana_nama = [
                    TeamMember.objects.get(id=int(pid)).name
                    for pid in pelaksana_ids.split(",") if pid.strip().isdigit()
                ]
                aktivitas.pelaksana = ", ".join(pelaksana_nama)
            else:
                aktivitas.pelaksana = "" # Set kosong jika tidak ada pelaksana yang dipilih

            aktivitas.save()
            messages.success(request, 'Aktivitas berhasil ditambahkan.')
            return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan.id)
        else:
            messages.error(request, 'Terjadi kesalahan saat menambahkan aktivitas. Mohon periksa kembali input Anda.')
    else:
        form = AktivitasForm()

    return render(request, 'proyek/form_aktivitas.html', {
        'form': form,
        'pekerjaan': pekerjaan,
        'anggota_list': anggota_list
    })

# ====== EDIT AKTIVITAS ======
def edit_aktivitas(request, aktivitas_id):
    """
    Mengedit aktivitas yang sudah ada berdasarkan ID aktivitas.
    Mencegah pengeditan jika proyek induk pekerjaan sudah 'Selesai'.
    Memperbarui detail aktivitas, termasuk pelaksana.
    """
    aktivitas = get_object_or_404(Aktivitas, id=aktivitas_id)
    pekerjaan = aktivitas.pekerjaan
    anggota_list = TeamMember.objects.all()

    # Cegah pengeditan jika proyek induk sudah selesai
    if pekerjaan.project.status == 'Selesai':
        messages.error(request, "Tidak bisa mengubah aktivitas karena proyek sudah ditutup.")
        return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan.id)

    if request.method == 'POST':
        form = AktivitasForm(request.POST, instance=aktivitas)
        if form.is_valid():
            aktivitas = form.save(commit=False)
            aktivitas.pekerjaan = pekerjaan # Pastikan aktivitas tetap terkait dengan pekerjaan yang sama

            # Mengelola pelaksana aktivitas dari input (mirip dengan tambah_aktivitas)
            pelaksana_ids = request.POST.get("pelaksana", "")
            if pelaksana_ids.strip():
                pelaksana_nama = [
                    TeamMember.objects.get(id=int(pid)).name
                    for pid in pelaksana_ids.split(",") if pid.strip().isdigit()
                ]
                aktivitas.pelaksana = ", ".join(pelaksana_nama)
            else:
                aktivitas.pelaksana = "" # Set kosong jika tidak ada pelaksana yang dipilih

            aktivitas.save()
            messages.success(request, 'Aktivitas berhasil diperbarui.')
            return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan.id)
        else:
            messages.error(request, 'Terjadi kesalahan saat memperbarui aktivitas. Mohon periksa kembali input Anda.')
    else:
        form = AktivitasForm(instance=aktivitas)

    return render(request, 'proyek/form_aktivitas.html', {
        'form': form,
        'pekerjaan': pekerjaan,
        'anggota_list': anggota_list,
        'aktivitas': aktivitas, # Kirim objek aktivitas untuk keperluan lain di template
    })

# ====== HAPUS AKTIVITAS ======
def hapus_aktivitas(request, aktivitas_id):
    """
    Menghapus aktivitas berdasarkan ID aktivitas.
    Mencegah penghapusan jika proyek induk pekerjaan sudah 'Selesai'.
    Setelah penghapusan, akan diarahkan kembali ke detail pekerjaan.
    """
    aktivitas = get_object_or_404(Aktivitas, id=aktivitas_id)
    proyek = aktivitas.pekerjaan.project
    pekerjaan_id = aktivitas.pekerjaan.id

    # Cegah penghapusan jika proyek sudah selesai
    if proyek.status == 'Selesai':
        messages.error(request, "Tidak bisa menghapus aktivitas karena proyek sudah ditutup.")
        return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan_id)

    aktivitas.delete()
    messages.success(request, 'Aktivitas berhasil dihapus.')
    return redirect('detail_pekerjaan', pekerjaan_id=pekerjaan_id)

# ====== TAMBAH ANGGOTA TIM ======
def tambah_anggota(request):
    """
    Menangani penambahan anggota tim baru.
    Menerima data form dan file foto dalam format Base64.
    Jika form valid, anggota tim akan disimpan, termasuk konversi dan penyimpanan foto.
    """
    if request.method == 'POST':
        form = TeamMemberForm(request.POST)
        photo_data = request.POST.get('photo_base64', '') # Ambil data foto Base64 dari input tersembunyi

        if form.is_valid():
            anggota = form.save(commit=False)
            if photo_data.startswith('data:image'):
                # Parsing data Base64 untuk mendapatkan format dan string gambar
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1] # Dapatkan ekstensi file (misal: 'png', 'jpeg')
                # Buat objek ContentFile dari data Base64 yang di-decode
                anggota.photo = ContentFile(base64.b64decode(imgstr), name=f"photo.{ext}")
            anggota.save()
            messages.success(request, 'Anggota tim berhasil ditambahkan.')
            return redirect('list_anggota')
        else:
            messages.error(request, 'Terjadi kesalahan saat menambahkan anggota. Mohon periksa kembali input Anda.')
    else:
        form = TeamMemberForm()
    return render(request, 'proyek/profil_anggota.html', {'form': form})

# ====== LIST SEMUA ANGGOTA ======
def list_anggota(request):
    """
    Menampilkan daftar semua anggota tim.
    Mendukung fungsionalitas pencarian berdasarkan nama anggota tim.
    """
    query = request.GET.get('q') # Ambil parameter query dari URL
    if query:
        # Filter anggota tim berdasarkan nama yang mengandung query (case-insensitive)
        anggota_list = TeamMember.objects.filter(name__icontains=query).order_by('name')
    else:
        # Jika tidak ada query, tampilkan semua anggota tim
        anggota_list = TeamMember.objects.all().order_by('name')
    return render(request, 'proyek/profile_team.html', {'anggota_list': anggota_list})

# ====== EDIT ANGGOTA ======
def edit_anggota(request, pk):
    """
    Mengedit detail anggota tim yang sudah ada berdasarkan primary key (pk).
    Menangani pembaruan data form dan pembaruan/penghapusan foto profil.
    """
    anggota = get_object_or_404(TeamMember, pk=pk)

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=anggota)
        photo_data = request.POST.get('photo_base64', '') # Ambil data foto Base64

        if form.is_valid():
            anggota = form.save(commit=False)
            # Logika untuk menangani foto:
            # 1. Jika photo_data kosong (berarti pengguna ingin menghapus foto)
            if photo_data == "":
                if anggota.photo: # Jika ada foto sebelumnya, hapus
                    anggota.photo.delete(save=False)
                anggota.photo = None # Set field photo menjadi null
            # 2. Jika photo_data berisi Base64 (berarti pengguna mengunggah foto baru)
            elif photo_data.startswith('data:image'):
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                anggota.photo = ContentFile(base64.b64decode(imgstr), name=f"photo.{ext}")
            # Jika photo_data tidak diubah (tidak kosong dan bukan Base64 baru), foto tidak akan diubah

            anggota.save()
            messages.success(request, 'Detail anggota tim berhasil diperbarui.')
            return redirect('list_anggota')
        else:
            messages.error(request, 'Terjadi kesalahan saat memperbarui anggota. Mohon periksa kembali input Anda.')
    else:
        form = TeamMemberForm(instance=anggota)

    return render(request, 'proyek/profil_anggota.html', {
        'form': form,
        'anggota': anggota # Kirim objek anggota untuk menampilkan foto saat ini
    })

# ====== HAPUS ANGGOTA ======
def hapus_anggota(request, pk):
    """
    Menghapus anggota tim berdasarkan primary key (pk).
    Setelah penghapusan, akan diarahkan kembali ke daftar anggota tim.
    """
    anggota = get_object_or_404(TeamMember, pk=pk)
    anggota.delete()
    messages.success(request, 'Anggota tim berhasil dihapus.')
    return redirect('list_anggota')

# ====== DETAIL ANGGOTA ======
def detail_anggota(request, pk):
    """
    Menampilkan detail anggota tim tertentu berdasarkan primary key (pk).
    """
    anggota = get_object_or_404(TeamMember, pk=pk)
    return render(request, 'proyek/detail_anggota.html', {'anggota': anggota})

# ====== CETAK PROYEK (PRINT VIEW) ======
def print_proyek(request, proyek_id):
    """
    Menampilkan halaman ringkasan proyek yang dirancang untuk dicetak,
    termasuk detail proyek, daftar pekerjaan, aktivitas, dan data dari API eksternal.
    """
    proyek = get_object_or_404(Project, id=proyek_id)
    # Mengambil anggota pelaksana proyek yang terkait
    pelaksana = ProjectMember.objects.filter(project=proyek).select_related("member")
    # Mengambil semua pekerjaan dan aktivitas terkait dalam proyek ini
    pekerjaan_list = proyek.pekerjaan.all().prefetch_related("aktivitas")

    # --- START NEW LOGIC FOR FETCHING EXTERNAL DATA ---
    # Inisialisasi dictionary untuk menyimpan data dari API eksternal
    external_data = {
        'ie': None, # Data dari Integrasi Eksternal (IE)
        'ic': None, # Data dari Integrasi C (IC)
        'imp_status': None, # Data status dari Integrasi P (IMP)
        'imp_detail': None, # Data detail dari Integrasi P (IMP)
    }

    # API Endpoints dari berbagai modul (disalin dari integrasi.html JS)
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
        """
        Fungsi utilitas untuk memformat string tanggal ISO 8601 menjadi format 'DD Bulan YYYY'.
        Menangani berbagai format ISO dan juga 'YYYY-MM-DD'.
        """
        if not iso_string:
            return 'N/A'
        try:
            # Mencoba memparsing ISO 8601, termasuk penanganan 'Z' (UTC)
            dt_obj = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            return dt_obj.strftime('%d %B %Y') # Contoh: 27 Juni 2025
        except ValueError:
            # Jika parsing ISO gagal, coba format YYYY-MM-DD
            if isinstance(iso_string, str) and iso_string.strip().count('-') == 2:
                try:
                    year, month, day = map(int, iso_string.split('-'))
                    dt_obj = datetime(year, month, day)
                    return dt_obj.strftime('%d %B %Y')
                except ValueError:
                    pass # Lanjutkan ke baris berikutnya jika gagal
            pass # Lanjutkan ke baris berikutnya jika gagal
        return iso_string # Kembalikan string asli jika semua parsing gagal

    # Mengambil data dari API IE (Integrasi Eksternal)
    try:
        ie_status_res = requests.get(api_endpoints['ie']['status'])
        ie_status_res.raise_for_status() # Akan memunculkan HTTPError untuk respons error (4xx/5xx)
        ie_detail_res = requests.get(api_endpoints['ie']['detail'])
        ie_detail_res.raise_for_status()

        ie_status_list = ie_status_res.json()
        ie_projek_list = ie_detail_res.json()

        # Mencari proyek yang relevan berdasarkan ID proyek aplikasi Anda
        external_data['ie'] = {
            'status': next((p for p in ie_status_list if p.get('id') == proyek.id), None),
            'detail': next((p for p in ie_projek_list if p.get('id_projek') == proyek.id), None),
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IE data for printing: {e}")
        messages.warning(request, f"Gagal mengambil data IE untuk cetak: {e}") # Opsional: tampilkan pesan ke user
    except json.JSONDecodeError as e:
        print(f"Error decoding IE JSON for printing: {e}")
        messages.warning(request, f"Gagal membaca format data IE untuk cetak: {e}")


    # Mengambil data dari API IC (Integrasi C)
    try:
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


    # Mengambil data dari API IMP (Integrasi P)
    try:
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

    # Mengirim semua data yang diperlukan ke template print_proyek.html
    return render(request, 'proyek/print_proyek.html', {
        'proyek': proyek, # Data proyek utama dari database Anda
        'pelaksana': pelaksana, # Anggota pelaksana proyek
        'pekerjaan_list': pekerjaan_list, # Daftar pekerjaan dan aktivitas terkait
        'external_data': external_data, # Data yang diambil dari API eksternal
    })

# ====== TUTUP PROYEK ======
@login_required
def tutup_proyek(request, proyek_id):
    """
    Menutup proyek tertentu.
    Jika metode permintaan adalah POST dan form valid, status proyek akan diubah menjadi 'Selesai'.
    Membutuhkan pengguna untuk login.
    """
    proyek = get_object_or_404(Project, id=proyek_id)

    if request.method == 'POST':
        form = TutupProyekForm(request.POST, request.FILES, instance=proyek)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.status = 'Selesai' # Ubah status proyek menjadi Selesai
            proyek.save()
            messages.success(request, "Proyek berhasil ditutup.")
            return redirect('homepage')
        else:
            messages.error(request, "Terjadi kesalahan. Pastikan semua data diisi dengan benar.")
    else:
        form = TutupProyekForm(instance=proyek)

    return render(request, 'proyek/tutup_proyek.html', {'form': form, 'proyek': proyek})

# ====== GRAFIK PROGRES PROYEK PER TAHUN ======
def progres_proyek(request):
    """
    Menampilkan grafik progres proyek berdasarkan tahun yang dipilih.
    Mengambil data proyek, memfilter berdasarkan tahun, dan mempersiapkan data dalam format JSON
    untuk digunakan oleh library grafik di frontend.
    """
    # Ambil tahun yang dipilih dari parameter GET, default ke tahun saat ini
    selected_year = int(request.GET.get("year", datetime.now().year))
    start_of_year = date(selected_year, 1, 1)
    end_of_year = date(selected_year, 12, 31)

    # Ambil semua proyek yang periodenya tumpang tindih dengan tahun yang dipilih
    semua_proyek = Project.objects.filter(
        start_date__lte=end_of_year, # Tanggal mulai harus sebelum atau pada akhir tahun
        end_date__gte=start_of_year # Tanggal selesai harus sesudah atau pada awal tahun
    )

    # Siapkan data proyek dalam format yang sesuai untuk JSON
    proyek_data = []
    for proyek in semua_proyek:
        proyek_data.append({
            "nama": proyek.name,
            "mulai": proyek.start_date.strftime('%Y-%m-%d'),
            "selesai": proyek.end_date.strftime('%Y-%m-%d'),
            "status": proyek.status
        })

    # Dapatkan semua tahun yang ada data proyeknya untuk filter dropdown
    all_years = Project.objects.aggregate(
        min_year=Min("start_date"),
        max_year=Max("end_date")
    )

    if all_years["min_year"] and all_years["max_year"]:
        years = list(range(all_years["min_year"].year, all_years["max_year"].year + 1))
    else:
        years = [selected_year] # Jika tidak ada proyek, tampilkan tahun saat ini saja

    context = {
        # Konversi data proyek ke JSON agar bisa digunakan di JavaScript frontend
        "data_proyek_json": json.dumps(proyek_data, cls=DjangoJSONEncoder),
        "selected_year": selected_year,
        "years": years,
    }

    return render(request, 'proyek/view_progress.html', context)

# ====== HALAMAN INTEGRASI ANTAR APLIKASI ======
@login_required
def integrasi_aplikasi(request):
    """
    Menampilkan halaman untuk mengelola integrasi antar aplikasi.
    Menampilkan daftar semua proyek yang ada. Membutuhkan pengguna untuk login.
    """
    projects = Project.objects.all()
    return render(request, 'proyek/integrasi.html', {'projects': projects})

# ====== API ENDPOINT UNTUK MANAJEMEN PROYEK (LENGKAP) ======
class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet API untuk model Project.
    Menyediakan operasi CRUD lengkap (list, retrieve, create, update, destroy)
    untuk objek Project melalui API REST.
    """
    queryset = Project.objects.all() # Queryset dasar untuk viewset ini
    serializer_class = ProjectSerializer # Serializer yang digunakan untuk konversi data
    permission_classes = [permissions.AllowAny] # Izin: memungkinkan akses tanpa otentikasi

    @action(detail=False, methods=['get'], url_path='status-only')
    def status_only(self, request):
        """
        Aksi kustom untuk mengembalikan daftar semua proyek hanya dengan informasi status.
        Accessible via: /api/projects/status-only/
        """
        projects = Project.objects.all()
        # Menggunakan serializer yang lebih ringan untuk hanya mengambil status
        serializer = ProjectStatusOnlySerializer(projects, many=True)
        return Response(serializer.data)