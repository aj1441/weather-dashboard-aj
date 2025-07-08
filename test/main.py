import importlib.util
import os
import sys

parent = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent)
spec = importlib.util.spec_from_file_location('parent_main', os.path.join(parent, 'main.py'))
parent_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent_main)
add_numbers = parent_main.add_numbers
convert_to_fahrenheit = parent_main.convert_to_fahrenheit
__all__ = ['add_numbers', 'convert_to_fahrenheit']
