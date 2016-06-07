import os
import sys
import socket

PROJECT_DIR = os.path.abspath(__file__)
sys.path.append(PROJECT_DIR)

if socket.gethostbyname(socket.gethostname()) == "4.4.4.4":
    import newrelic.agent
    newrelic.agent.initialize('/home/mfi/newrelic.ini')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "microfinance.settings_server")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "microfinance.settings_local")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
