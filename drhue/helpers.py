from copy import deepcopy
from dataclasses import field


def default_field(default):
    return field(default_factory=lambda: deepcopy(default))
