"""
ASGI config for district_events project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'district_events.settings')
application = get_asgi_application()
