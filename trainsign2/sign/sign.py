import os
from typing import Optional

from serial import Serial

from trainsign2.util.config import load_config


class Sign:
    config: str
    serial: Serial

    def __init__(self, config: Optional[os.PathLike]):
        self.config = load_config(config)
        self.serial = Serial(**self.config.serial.model_dump())
        self.serial.write(b"We're no strangers|to looooove...")
