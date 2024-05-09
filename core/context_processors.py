from django.conf import settings as django_settings
# from django.templatetags.static import static
# import hashlib
# import os


def settings(request):
    return {
        "settings": django_settings,
    }
# def static_version(request):
#     static_url = static('')
#     file_path = os.path.join(django_settings.STATIC_ROOT, static_url)
#     version = hashlib.md5(os.path.getmtime(file_path).encode()).hexdigest()
#     return f"?v={version}"

