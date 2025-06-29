# proyek/templatetags/my_custom_filters.py
from django import template
from django.template.defaultfilters import stringfilter
from datetime import datetime # Import datetime untuk format tanggal
import ast # Import ast untuk mengurai string Python dict

register = template.Library()

@register.filter
@stringfilter
def replace_underscore_with_space(value):
    """Mengganti underscore dengan spasi dan membuat setiap kata menjadi Title Case."""
    return value.replace('_', ' ').title() # Gunakan .title() agar setiap kata diawali kapital

@register.filter
@stringfilter
def format_iso_date_for_print(iso_string):
    """Memformat string tanggal ISO (YYYY-MM-DD atau ISO lengkap) menjadi 'DD Bulan YYYY'."""
    if not iso_string:
        return 'N/A'
    try:
        # Coba parse sebagai ISO 8601 lengkap (termasuk waktu dan timezone)
        dt_obj = datetime.fromisoformat(iso_string.replace('Z', '+00:00')) # Ganti 'Z' untuk kompatibilitas
        return dt_obj.strftime('%d %B %Y') # Contoh: 27 Juni 2025
    except ValueError:
        # Jika bukan ISO lengkap, coba parse sebagai YYYY-MM-DD
        if isinstance(iso_string, str) and iso_string.strip().count('-') == 2:
            try:
                year, month, day = map(int, iso_string.split('-'))
                dt_obj = datetime(year, month, day)
                return dt_obj.strftime('%d %B %Y')
            except ValueError:
                pass # Lanjut ke default return
        pass # Lanjut ke default return
    return iso_string # Kembalikan string asli jika tidak bisa di-parse

@register.filter
def parse_python_dict_string(value):
    """Mengurai string representasi dictionary Python (misal: "{'key': 'val'}") menjadi dictionary Python.
    Lebih aman daripada eval()."""
    if not isinstance(value, str):
        return value # Jika bukan string, kembalikan saja
    try:
        # ast.literal_eval lebih aman daripada eval() untuk string dari sumber eksternal
        # Ini akan mengubah "{'key': 'value'}" menjadi {'key': 'value'}
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return {} # Kembalikan dictionary kosong jika parsing gagal