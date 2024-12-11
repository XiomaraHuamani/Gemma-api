#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import locale


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # Fuerza UTF-8 en el entorno
os.environ["PYTHONIOENCODING"] = "utf-8"  # Garantiza que la entrada/salida de Python sea UTF-8

