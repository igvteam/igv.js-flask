import os

basedir = os.path.abspath(os.path.dirname(__file__))

ALLOWED_EMAILS = "allowed_emails.txt"
USES_OAUTH = False
PUBLIC_DIR = "/static/data/public"
ENABLE_CORS_REQUESTS = False

ENABLE_ALIGNMENT_SERVICE = True
ENABLE_UCSC_SERVICE = True

DEBUG = True
