"""Ponto de entrada WSGI.

O Gunicorn e o mod_wsgi do Apache importam a variável application deste
arquivo e chamam a função a cada pedido.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_mural.settings')

application = get_wsgi_application()
