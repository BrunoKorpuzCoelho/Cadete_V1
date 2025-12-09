"""
WSGI Entry Point
================

This file serves as the entry point for WSGI servers like Gunicorn.

Usage with Gunicorn:
    gunicorn -c gunicorn_config.py wsgi:app
"""

import sys
sys.dont_write_bytecode = True

from app import app

if __name__ == "__main__":
    app.run()
