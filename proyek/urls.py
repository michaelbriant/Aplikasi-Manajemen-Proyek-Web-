from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('tambah-proyek/', views.tambah_proyek, name='tambah_proyek'),
    path('tambah-anggota/', views.tambah_anggota, name='tambah_anggota'),
    path('edit_proyek/<int:pk>/', views.edit_proyek, name='edit_proyek'),
    path('hapus/<int:pk>/', views.hapus_proyek, name='hapus_proyek'),
    path('profile-team/', views.list_anggota, name='list_anggota'),
    path('edit-anggota/<int:pk>/', views.edit_anggota, name='edit_anggota'),
    path('hapus-anggota/<int:pk>/', views.hapus_anggota, name='hapus_anggota'),
    path('detail-anggota/<int:pk>/', views.detail_anggota, name='detail_anggota'),
]
