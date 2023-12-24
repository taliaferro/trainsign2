import os
from logging import BASIC_FORMAT
from typing import Sequence, Union, Mapping

from yaml import safe_load
from pydantic import BaseModel, Field, FilePath, HttpUrl, Extra, field_serializer
from jinja2 import Template


def load_config(path: os.PathLike):
    with open(path, "r") as config_fh:
        return Config(**safe_load(config_fh))

# TODO add filter config schema

class LogFormatterConfig(BaseModel):
    format: str = "%(asctime)s %(name)s %(levelname)s: %(message)"
    datefmt: str = "%Y-%m-%dT%H:%M:%S%z"  # timezone-aware ISO8601
    style: str = "%"
    validate_field: bool = Field(default=True, alias="validate")


class LogHandlerConfig(BaseModel):
    class Config:
        extra = Extra.allow

    handler_class: str = Field(alias="class", default="logging.StreamHandler")
    level: str = "INFO"
    formatter: str = "default"
    filters: list[str] = []


class LoggerConfig(BaseModel):
    level: str = "INFO"
    propagate: bool = True
    filters: list[str] = []
    handlers: list[str] = []


class LoggingSystemConfig(BaseModel):
    version: int = 1
    disable_existing_loggers: bool = True
    incremental: bool = False
    formatters: dict[str, LogFormatterConfig] = {"default": LogFormatterConfig()}
    handlers: dict[str, LogHandlerConfig] = {
        "default": LogHandlerConfig(formatter="default")
    }
    loggers: dict[str, LoggerConfig] = {}
    root: LoggerConfig = LoggerConfig(handlers=['default'])


class SerialConfig(BaseModel):
    # could need the rest of the parameters in other use cases,
    # but these two are enough to get it working with an Arduino
    port: str
    baudrate: int = 9600


class ClientConfig(BaseModel):
    # these are the only ones we need to configure right now
    # come back here if the API changes
    url: HttpUrl = "https://api.511.org"
    agency: str = "SF"
    api_key: str = None
    rate_limit: int = 60
    limit_remaining: int = 60

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
    logging: LoggingSystemConfig = LoggingSystemConfig()
