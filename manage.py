#!/usr/bin/env python
import os
import sys
import socket

if __name__ == "__main__":
    if socket.gethostbyname(socket.gethostname()) == "4.4.4.4":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "microfinance.settings_server")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "microfinance.settings_local")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
