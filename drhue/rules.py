from __future__ import annotations

from abc import abstractmethod, ABC

from loguru import logger

from drhue import times


class Rule(ABC):
    def __init__(self, entity):
        self.entity = entity

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
        rules_initialised = [rule(entity) for rule in self.rules]
        self.rules_sorted = sorted(rules_initialised, key=lambda rule: self.context.times.get(rule.start))
        if len(self.rules_sorted):
            if self.rules_sorted[0].start != times.day_start:
                logger.warning(f"Rules for {self} should begin from day start.")
            for i, rule in enumerate(self.rules_sorted[1:]):
                if rule.start != self.rules_sorted[i].end:
                    logger.warning(f"Rule {rule} should start when previous rule ends.")
            if self.rules_sorted[-1].end != times.day_end:
                logger.warning(f"Rules for {self} should end on day end.")

    def apply(self):
        for rule in self.rules_sorted:
            if self.context.times.get(rule.start) < self.times.now <= self.context.times.get(rule.end):
                logger.debug(f"Rule {rule} is active.")
                rule.apply()
                break
