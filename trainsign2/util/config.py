import os
from typing import Sequence, Union, Mapping

from yaml import safe_load
from pydantic import BaseModel, FilePath, HttpUrl, field_serializer
from jinja2 import Template


def load_config(path: os.PathLike):
    with open(path, "r") as config_fh:
        return Config(**safe_load(config_fh))


class SerialConfig(BaseModel):
    # could need the rest of the parameters in other use cases,
    # but these two are enough to get it working with an Arduino
    port: str
    baudrate: int = 9600


class ClientConfig(BaseModel):
    # these are the only ones we need to configure right now
    # come back here if the API changes
    url: HttpUrl = "https://api.511.org",
    agency: str = "SF",
    api_key: str = None,
    rate_limit: int = 60,
    limit_remaining: int = 60,

    @field_serializer("url")
    def url_is_string(url):
        return str(url)

class Screen(BaseModel):
    template: str
    duration: int = 3
    context: dict = {}



class Config(BaseModel):
    client: ClientConfig
    serial: SerialConfig
    init: Sequence[Screen]
    loop: Sequence[Screen]
