import os
from typing import Sequence

from yaml import safe_load
from pydantic import BaseModel, FilePath


def load_config(path: os.PathLike):
    with open(path, "r") as config_fh:
        return Config(**safe_load(config_fh))


class SerialConfig(BaseModel):
    # could need the rest of the parameters in other use cases,
    # but these two are enough to get it working with an Arduino
    port: str
    baudrate: int = 9600


class Config(BaseModel):
    serial: SerialConfig
    init: Sequence[str]
    loop: Sequence[str]
