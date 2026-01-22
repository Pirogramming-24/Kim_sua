"""
WSGI config for pirostagram project.

It exposes the WSGI callable as a module-level variable named "application".
"""

import os
from django.core.wsgi import get_wsgi_application

# settings 모듈 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# WSGI application 객체 생성
application = get_wsgi_application()
