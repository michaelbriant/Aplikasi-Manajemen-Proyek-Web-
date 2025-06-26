# Mengimpor AppConfig dari Django
from django.apps import AppConfig


# Konfigurasi aplikasi 'proyek'
class ProyekConfig(AppConfig):
    # Menentukan tipe default untuk primary key otomatis di model adalah BigAutoField
    default_auto_field = 'django.db.models.BigAutoField'

    # Menyebutkan nama aplikasi ini, sesuai dengan foldernya
    name = 'proyek'
