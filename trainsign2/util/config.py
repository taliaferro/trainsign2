import os
from typing import Sequence

from yaml import safe_load
from pydantic import BaseModel, HttpUrl


def load_config(path: os.PathLike):
    with open(path, "r") as config_fh:
        return Config(**safe_load(config_fh))


class Config(BaseModel):
    init: Sequence[str]
    loop: Sequence[str]
