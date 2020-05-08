from unittest.mock import MagicMock

from drhue.entities.base import Entity
from drhue.rules import Rules


def test_attach_context_to_entities():
    entity_1 = Entity('1')
    entity_2 = Entity('2', sub_entities=[entity_1])
    entity_3 = Entity('3', sub_entities=[entity_2])

    context = MagicMock()
    entity_3.attach_context(context)

    assert entity_3.context == context
    assert entity_2.context == context
    assert entity_1.context == context


def test_sync_entity_states():
    entity_1 = Entity('1')
    entity_1._sync_states = MagicMock()
    entity_2 = Entity('2', sub_entities=[entity_1])
    entity_2._sync_states = MagicMock()
    entity_3 = Entity('3', sub_entities=[entity_2])
    entity_3._sync_states = MagicMock()

    entity_3.sync_states()

    entity_1._sync_states.assert_called_once()
    entity_2._sync_states.assert_called_once()
    entity_3._sync_states.assert_called_once()


def test_rules_gathering():
    def gen_rule(n):
        class RuleN(Rules):
            priority = n
            rules = []
            def apply(self):
                pass

        return RuleN

    rule_1 = gen_rule(1)
    rule_2 = gen_rule(2)
    rule_3 = gen_rule(3)
    rule_4 = gen_rule(4)
    rule_5 = gen_rule(5)
    rule_6 = gen_rule(6)

    entity_1 = Entity('1', rules=[rule_1, rule_6], context=MagicMock())
    entity_2 = Entity('2', sub_entities=[entity_1], rules=[rule_2, rule_5], context=MagicMock())
    entity_3 = Entity('3', sub_entities=[entity_2], rules=[rule_3, rule_4], context=MagicMock())

    assert [rule.priority for rule in entity_3.gather_rules()] == [3, 4, 2, 5, 1, 6]
    assert [rule.priority for rule in entity_3.sorted_rules] == [1, 2, 3, 4, 5, 6]
