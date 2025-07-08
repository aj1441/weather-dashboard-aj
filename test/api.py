import importlib.util
import os
import sys

parent = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent)
spec = importlib.util.spec_from_file_location('parent_api', os.path.join(parent, 'api.py'))
parent_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent_api)
fetch_weather = parent_api.fetch_weather
requests = parent_api.requests
__all__ = ['fetch_weather']
