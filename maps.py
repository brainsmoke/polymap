
import os


def list_maps():
    files = os.listdir(os.path.join(os.path.dirname(__file__), 'maps'))
    return [x[:x.rfind('.paths')] for x in files if x.endswith('.paths')]


def map_file(name):
    return os.path.join(os.path.dirname(__file__), 'maps', name + '.paths')
