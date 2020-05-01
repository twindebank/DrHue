from __future__ import annotations

from abc import ABCMeta
from dataclasses import dataclass, field
from typing import Type, List, Any, Optional, Dict

from loguru import logger

from drhue.adapter.base import DrHueAdapter
from drhue.context import Context
from drhue.rule import Rule


@dataclass
class Entity(metaclass=ABCMeta):
    name: str
    rules: List[Type[Rule]] = field(default_factory=list)
    sub_entities: List[Type[Entity]] = field(default_factory=list)

    context: Context = None
    _sorted_rules: List[Type[Rule]] = None

    def __hash__(self):
        return hash(self.name)

    def gather_rules(self):
        rules = []
        for sub_entity in self.sub_entities:
            rules.extend(sub_entity.gather_rules())
        return rules

    def sync_states(self):
        for entity in self.sub_entities:
            entity.sync_states()

    def attach_context(self, context: Context):
        self.context = context
        for sub_entity in self.sub_entities:
            sub_entity.attach_context(context)

    @property
    def sorted_rules(self) -> List[Type[Rule]]:
        if self._sorted_rules is None:
            self._sorted_rules = sorted(self.gather_rules(), key=lambda rule: rule.priority)
        return self._sorted_rules


@dataclass()
class AdapterProperty:
    name: str
    value_type: Type
    default: Optional[value_type] = None
    read_only: bool = False
    value: Any = default


@dataclass
class HueEntity(Entity, metaclass=ABCMeta):
    """
    name must be tied to hue entity
    """
    adapter_properties: List[AdapterProperty] = None
    adapter: DrHueAdapter = None
    _adapter_class: Type[DrHueAdapter] = None
    _adapter_property_dict: Dict = None


    def attach_context(self, context: Context):
        """

        todo: here
        something funky with this being called twice, once properly once not


        :param context:
        :return:
        """
        super().attach_context(context)
        self.adapter = self._adapter_class(self.context.bridge, self.name)
        self._adapter_property_dict = {prop.name: prop for prop in self.adapter_properties}

    def sync_state(self):
        for prop in self.adapter_properties:
            if not prop.read_only and not self._check_consistency(prop):
                self.set(prop.name, getattr(self.adapter, prop.name))

    def set(self, prop, val):
        if self._adapter_property_dict[prop].read_only:
            raise ValueError(f"Cannot mutate read only property '{prop}' for '{self.name}'.")
        self._adapter_property_dict[prop] = val

    def read(self, prop):
        return self._adapter_property_dict[prop]

    def _check_consistency(self, prop):
        entity_state = self.read(prop)
        adapter_state = getattr(self.adapter, prop)
        if adapter_state != entity_state:
            logger.warning(
                f"Inconsistent state in '{self.name}' for property '{prop}':"
                f"\n\tentity: {entity_state}\n\tadapter: {adapter_state}"
            )
            return False
        return True
