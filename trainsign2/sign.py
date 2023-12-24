import os
import logging
import logging.config
import asyncio
from typing import Optional, Iterable

from serial import Serial
from jinja2 import Environment, Template

from trainsign2.client import Open511Client
from trainsign2.util.config import load_config, Config, Screen
from trainsign2.util.helpers import time_format


def _prepare_msg(message: str):
    message = message.replace("\n", "|")
    if "|" not in message:
        message += "|"
    return message.encode()


class Sign:
    config: Config

    def __init__(self, config: Optional[os.PathLike]):
        self.config = load_config(config)

        logging.config.dictConfig(self.config.logging.model_dump(by_alias=True))

        self._logger = logging.getLogger(__name__)

        self._serial = Serial(**self.config.serial.model_dump())
        self._template_environment = Environment()
        self._template_environment.globals["now"] = time_format

        self._client = Open511Client(**self.config.client.model_dump())

        self.init_screens = [self._load_screen(screen) for screen in self.config.init]
        self.loop_screens = [self._load_screen(screen) for screen in self.config.loop]

        self.arrivals = []

    async def start(self):
        init_tasks = [
            self._show_screens(self.init_screens),
            self._update_arrivals_cache(),
        ]
        forever_tasks = [self._update_loop(), self._display_loop()]

        self._logger.info("Running initialization tasks")
        await asyncio.gather(*init_tasks)
        self._logger.info("Running repeated tasks")
        await asyncio.gather(*forever_tasks)

    async def _display_loop(self):
        while True:
            await self._show_screens(self.loop_screens)

    async def _update_loop(self):
        while True:
            await self._update_arrivals_cache()

    async def _update_arrivals_cache(self):
        latest_monitoring = self._client.stop_monitoring()
        self._logger.info("Updating arrivals cache...")
        self.arrivals = latest_monitoring["ServiceDelivery"]["StopMonitoringDelivery"][
            "MonitoredStopVisit"
        ]

    def _load_screen(self, screen: Screen):
        template = self._template_environment.from_string(screen.template)
        return screen, template

    async def _show_screens(self, screens: Iterable[tuple[Screen, Template]]):
        for screen, template in screens:
            await self._show_screen(screen, template)

    async def _show_screen(self, screen: Screen, template: Template):
        self._logger.info("Displaying screen {}".format(screen.template))
        self.write(template.render(context=screen.context))
        await asyncio.sleep(screen.duration)

    def write(self, message: str):
        self._serial.write(_prepare_msg(message))
