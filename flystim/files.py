from pathlib import Path

def top_dir():
    return Path(__file__).resolve().parent.parent

def rel_path(*args):
    return Path(top_dir(), *args)