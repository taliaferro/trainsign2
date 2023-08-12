import os

def load_config(path: os.PathLike):
    with open(path, "r") as config_fh:
        return config_fh.read()
