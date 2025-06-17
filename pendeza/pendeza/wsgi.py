import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pendeza.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()