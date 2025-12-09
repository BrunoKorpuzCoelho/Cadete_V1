"""
Gunicorn Configuration File
============================

Production WSGI server configuration for Flask application.

Usage:
    gunicorn -c gunicorn_config.py app:app
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'cadete_app'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/key.pem'
# certfile = '/path/to/cert.pem'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("=" * 60)
    print("Starting Cadete Application with Gunicorn")
    print("=" * 60)
    print(f"Workers: {workers}")
    print(f"Bind: {bind}")
    print(f"Timeout: {timeout}s")
    print("=" * 60)

def on_reload(server):
    """Called to recycle workers during a reload."""
    print("Reloading workers...")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    print(f"Worker {worker.pid} received SIGINT/SIGQUIT")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    print(f"Worker {worker.pid} received SIGABRT")
