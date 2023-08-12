import os
from typing import Optional

from trainsign2.util.config import load_config


class Sign:
    config: str

    def __init__(self, config: Optional[os.PathLike]):
        self.config = load_config(config)
