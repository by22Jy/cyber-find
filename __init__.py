# __init__.py в корне проекта
import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Реэкспортируем основные модули
from cyberfind_cli import main as cli_main
from cyberfind_gui import main as gui_main
from cyberfind_api import main as api_main

__all__ = ['cli_main', 'gui_main', 'api_main']