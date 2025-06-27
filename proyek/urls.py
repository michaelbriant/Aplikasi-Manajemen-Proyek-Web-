from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path, include
# from .views import ProjectStatusOnlyAPIView # <-- BARIS INI DIHAPUS

urlpatterns = [
    # ===== Beranda utama aplikasi =====
    path('', views.homepage, name='homepage'),

    # ===== Autentikasi Pengguna =====
    path('login/', views.login_view, name='login'),          # Form login
    path('logout/', views.custom_logout, name='logout'),      # Logout custom
    path('register/', views.register, name='register'),       # Form registrasi pengguna baru

    # ===== Reset Password (Tanpa Email) =====
    path('reset-password/', views.reset_password_email_view, name='reset_password_email'),     # Step 1: input email
    path('set-new-password/<int:user_id>/', views.set_new_password_view, name='set_new_password'), # Step 2: atur password baru

    # ===== Manajemen Proyek =====
    path('tambah-proyek/', views.tambah_proyek, name='tambah_proyek'),      # Form tambah proyek baru
    path('edit_proyek/<int:pk>/', views.edit_proyek, name='edit_proyek'),    # Form edit proyek
    path('hapus/<int:pk>/', views.hapus_proyek, name='hapus_proyek'),        # Hapus proyek
    path('print_proyek/<int:proyek_id>/', views.print_proyek, name='print_proyek'),  # Cetak detail proyek
    path('progress/', views.progres_proyek, name='progres_proyek'),          # Lihat progres seluruh proyek
    path('proyek/<int:proyek_id>/tutup/', views.tutup_proyek, name='tutup_proyek'),   # Form penutupan proyek

    # ===== Manajemen Anggota Tim =====
    path('tambah-anggota/', views.tambah_anggota, name='tambah_anggota'),          # Tambah anggota tim
    path('profile-team/', views.list_anggota, name='list_anggota'),             # Daftar seluruh anggota
    path('edit-anggota/<int:pk>/', views.edit_anggota, name='edit_anggota'),      # Edit data anggota
    path('hapus-anggota/<int:pk>/', views.hapus_anggota, name='hapus_anggota'),    # Hapus anggota tim
    path('detail-anggota/<int:pk>/', views.detail_anggota, name='detail_anggota'),  # Detail lengkap anggota

    # ===== Manajemen Pekerjaan dan Aktivitas =====
    path('proyek/<int:proyek_id>/pekerjaan/', views.daftar_pekerjaan, name='daftar_pekerjaan'),          # Daftar pekerjaan per proyek
    path('proyek/<int:proyek_id>/pekerjaan/tambah/', views.tambah_pekerjaan, name='tambah_pekerjaan'),   # Tambah pekerjaan
    path('pekerjaan/<int:pk>/edit/', views.edit_pekerjaan, name='edit_pekerjaan'),                      # Edit pekerjaan
    path('pekerjaan/<int:pk>/hapus/', views.hapus_pekerjaan, name='hapus_pekerjaan'),                   # Hapus pekerjaan
    path('pekerjaan/<int:pekerjaan_id>/', views.detail_pekerjaan, name='detail_pekerjaan'),             # Lihat detail pekerjaan
    path('pekerjaan/<int:pekerjaan_id>/aktivitas/tambah/', views.tambah_aktivitas, name='tambah_aktivitas'), # Tambah aktivitas ke pekerjaan
    path('aktivitas/<int:aktivitas_id>/edit/', views.edit_aktivitas, name='edit_aktivitas'),             # Edit aktivitas
    path('aktivitas/<int:aktivitas_id>/hapus/', views.hapus_aktivitas, name='hapus_aktivitas'),          # Hapus aktivitas

    # ===== Profil dan Pengaturan Akun =====
    path('profile/', views.profile_user, name='profile_user'),      # Halaman profil pengguna

    # ===== Integrasi Antar Modul =====
    path('pesan/', views.integrasi_aplikasi, name='integrasi'),     # Halaman integrasi pengiriman & status antar modul
    # path('status-only/', ProjectStatusOnlyAPIView.as_view(), name='status-only'), # <-- BARIS INI DIHAPUS (duplikasi dengan API)

    path('api/', include('proyek.api_urls')),
]