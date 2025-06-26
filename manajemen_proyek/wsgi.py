"""
WSGI config for manajemen_proyek project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# -----------------------------------------
# Menentukan file settings Django yang akan digunakan
# Ini penting saat server WSGI memulai aplikasi
# -----------------------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manajemen_proyek.settings')

# -----------------------------------------
# Membuat instance WSGI application yang akan digunakan oleh server
# seperti Gunicorn, uWSGI, atau server lain yang kompatibel dengan WSGI
# -----------------------------------------
application = get_wsgi_application()
