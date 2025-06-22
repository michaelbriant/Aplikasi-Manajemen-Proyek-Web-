from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from proyek import views
from django.contrib.auth.views import LogoutView
from .views import ProjectStatusOnlyAPIView

urlpatterns = [
    path('', views.homepage, name='homepage'),

    # Login
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),

    path('reset-password/', views.reset_password_email_view, name='reset_password_email'),
    path('set-new-password/<int:user_id>/', views.set_new_password_view, name='set_new_password'),

    # Proyek
    path('tambah-proyek/', views.tambah_proyek, name='tambah_proyek'),
    path('edit_proyek/<int:pk>/', views.edit_proyek, name='edit_proyek'),
    path('hapus/<int:pk>/', views.hapus_proyek, name='hapus_proyek'),
    path('print_proyek/<int:proyek_id>/', views.print_proyek, name='print_proyek'),
    path('progress/', views.progres_proyek, name='progres_proyek'),
    path('proyek/<int:proyek_id>/tutup/', views.tutup_proyek, name='tutup_proyek'),

    # Anggota
    path('tambah-anggota/', views.tambah_anggota, name='tambah_anggota'),
    path('profile-team/', views.list_anggota, name='list_anggota'),
    path('edit-anggota/<int:pk>/', views.edit_anggota, name='edit_anggota'),
    path('hapus-anggota/<int:pk>/', views.hapus_anggota, name='hapus_anggota'),
    path('detail-anggota/<int:pk>/', views.detail_anggota, name='detail_anggota'),

    # Pekerjaan & Aktivitas
    path('proyek/<int:proyek_id>/pekerjaan/', views.daftar_pekerjaan, name='daftar_pekerjaan'),
    path('proyek/<int:proyek_id>/pekerjaan/tambah/', views.tambah_pekerjaan, name='tambah_pekerjaan'),
    path('pekerjaan/<int:pk>/edit/', views.edit_pekerjaan, name='edit_pekerjaan'),
    path('pekerjaan/<int:pk>/hapus/', views.hapus_pekerjaan, name='hapus_pekerjaan'),
    path('pekerjaan/<int:pekerjaan_id>/', views.detail_pekerjaan, name='detail_pekerjaan'),
    path('pekerjaan/<int:pekerjaan_id>/aktivitas/tambah/', views.tambah_aktivitas, name='tambah_aktivitas'),
    path('aktivitas/<int:aktivitas_id>/edit/', views.edit_aktivitas, name='edit_aktivitas'),
    path('aktivitas/<int:aktivitas_id>/hapus/', views.hapus_aktivitas, name='hapus_aktivitas'),

    # Profile & Settings
    path('profile/', views.profile_user, name='profile_user'),

    # integrasi
    path('pesan/', views.integrasi_aplikasi, name='integrasi'),
    path('status-only/', ProjectStatusOnlyAPIView.as_view(), name='status-only'),
]
