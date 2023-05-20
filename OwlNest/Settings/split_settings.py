from split_settings.tools import include
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


include(
    'base.py',
    'local.py',
)