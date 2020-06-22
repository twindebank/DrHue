from abc import ABC
from dataclasses import dataclass

from drhue.entities.base import Entity


@dataclass
class GoogleEntity(Entity, ABC):
    pass


@dataclass
class GoogleHome(GoogleEntity):
    pass


@dataclass
class Chromecast(GoogleEntity):
    pass


@dataclass
class Vacuum(GoogleEntity):
    pass
