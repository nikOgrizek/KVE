import json
import os
import sys

DATA_FILE = 'turbines.json'

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_turbines():
    data_file_path = resource_path(DATA_FILE)
    if not os.path.exists(data_file_path):
        return []
    with open(data_file_path, 'r') as file:
        return json.load(file)

def save_turbines(turbines):
    data_file_path = resource_path(DATA_FILE)
    with open(data_file_path, 'w') as file:
        json.dump(turbines, file, indent=4)
