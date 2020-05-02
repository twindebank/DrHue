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
    sub_entities: List[Entity] = field(default_factory=list)
    context: Context = None

    _sorted_rules: List[Rule] = None

    def __hash__(self):
        return hash(self.name)

    def gather_rules(self) -> List[Rule]:
        rules = [rule(entity=self) for rule in self.rules]
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
    def sorted_rules(self) -> List[Rule]:
        if self._sorted_rules is None:
            self._sorted_rules = sorted(self.gather_rules(), key=lambda rule: rule.priority)
        return self._sorted_rules


@dataclass()
class EntityProperty:
    name: str
    value_type: Type
    default: Optional[value_type] = None
    read_only: bool = False
    value: Any = None

    def __post_init__(self):
        if self.value is None:
            self.set(self.default)

    def set(self, val):
        self.value = val

    def read(self):
        return self.value


@dataclass
class HueEntity(Entity, metaclass=ABCMeta):
    """
    name must be tied to hue entity
    """
    _entity_properties: List[EntityProperty] = None
    _adapter: DrHueAdapter = None
    _entity_property_dict: Dict = None
    _adapter_class: Type[DrHueAdapter] = None

    def __post_init__(self):
        self._entity_property_dict = {prop.name: prop for prop in self._entity_properties}

    def attach_context(self, context: Context):
        super().attach_context(context)
        self._adapter = self._adapter_class(bridge=self.context.bridge, name=self.name)

    def sync_states(self):
        super().sync_states()
        for prop in self._entity_properties:
            adapter_state = getattr(self._adapter, prop.name)
            entity_state = prop.read()
            if not prop.read_only and entity_state != adapter_state:
                logger.warning(
                    f"Inconsistent state in '{self.name}' for property '{prop.name}':"
                    f"\n\tentity: {entity_state}\n\tadapter: {adapter_state}"
                )
            prop.set(adapter_state)

    def set(self, prop_name, val):
        entity_property = self._entity_property_dict[prop_name]
        if entity_property.read_only:
            raise ValueError(f"Cannot mutate read only property '{prop_name}' for '{self.name}'.")
        entity_property.set(val)
        setattr(self._adapter, prop_name, val)

    def read(self, prop):
        return self._entity_property_dict[prop].read()
