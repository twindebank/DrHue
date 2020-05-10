from __future__ import annotations

from abc import abstractmethod, ABC

from loguru import logger

from drhue import times
from drhue.state import State, get_obj_fqn

AUTO = 'auto'
ENABLE = 'enable'
DISABLE = 'disable'


class Rule(ABC):
    def __init__(self, entity):
        self.entity = entity
        fqn_partial = get_obj_fqn(self).split('.')[-2:]
        self.fqn = fqn_partial[0] + '.rules.' + fqn_partial[1]

    @property
    @abstractmethod
    def start(self) -> times.Time:
        pass

    @property
    @abstractmethod
    def end(self) -> times.Time:
        pass

    @abstractmethod
    def apply(self):
        pass


class Rules(ABC):
    priority = 0

    @property
    @abstractmethod
    def rules(self):
        pass

    def __init__(self, entity):
        self.entity = entity
        self.context = entity.context
        self.times = entity.context.times
        self.state = State()
        rules_initialised = [rule(entity) for rule in self.rules]
        self.rules_sorted = sorted(rules_initialised, key=lambda rule: self.context.times[rule.start])
        if len(self.rules_sorted):
            if self.rules_sorted[0].start != times.day_start:
                logger.warning(f"Rules for {self} should begin from day start.")
            for i, rule in enumerate(self.rules_sorted[1:]):
                if rule.start != self.rules_sorted[i].end:
                    logger.warning(f"Rule {rule} should start when previous rule ends.")
            if self.rules_sorted[-1].end != times.day_end:
                logger.warning(f"Rules for {self} should end on day end.")

            for rule in self.rules_sorted:
                self.state.setdefault(f"{rule.fqn}.state", AUTO)

    def apply(self):
        for rule in self.rules_sorted:
            rule_state = self.state[f"{rule.fqn}.state"]
            self.state[f"{rule.fqn}.active"] = \
                self.context.times[rule.start] < self.times.now <= self.context.times[rule.end]

            if rule_state == DISABLE:
                continue

            if rule_state == AUTO and self.state[f"{rule.fqn}.active"] or rule_state == ENABLE:
                logger.debug(f"Rule {rule.fqn} is active.")
                rule.apply()
