import os
#sys.path.insert(0, '/home/aon24/sova-online/venv/bin')
#sys.path.insert(0, '/home/aon24/sova-online')
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arm.settings')
application = get_wsgi_application()
