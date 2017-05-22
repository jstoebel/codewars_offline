import os
this_file_abs = (os.path.abspath(__file__))

PROJECT_ROOT = os.path.dirname(this_file_abs)
TEMPLATES = os.path.join(PROJECT_ROOT, 'templates')
