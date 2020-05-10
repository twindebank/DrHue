import pytest
from pytest_assume.plugin import assume

from drhue.server.formatting import create_nested_dict_from_period_separated_keys, nested_dict_to_html


def test_create_nested_dict_from_period_separated_keys():
    test_cases = [
        (
            {
                'a': 1,
                'b': 2
            },
            {
                'a': 1,
                'b': 2
            }
        ),
        (
            {
                'a.a': 1,
                'a.b': 2,
            },
            {
                'a': {
                    'a': 1,
                    'b': 2
                }
            }
        ),
        (
            {
                'a.a.a': 111,
                'a.a.b': 112,
                'a.b.b': 122,
                'a.b.c': 123,
                'a.c.c': 133,
                'c.c.c': 333,
            },
            {
                'a': {
                    'a': {
                        'a': 111,
                        'b': 112
                    },
                    'b': {
                        'b': 122,
                        'c': 123
                    },
                    'c': {
                        'c': 133
                    },
                },
                'c': {
                    'c': {
                        'c': 333
                    }
                }
            }
        )
    ]
    for (d, expected) in test_cases:
        actual = create_nested_dict_from_period_separated_keys(d)
        assert actual == expected


def test_create_nested_dict_from_period_separated_keys_fails_when_overwrite_key():
    test_cases = [
        {
            'a': 1,
            'a.b': 2
        },
        {
            'a.b': 1,
            'a': 2
        }
    ]
    for tc in test_cases:
        with pytest.raises(ValueError) as exc:
            create_nested_dict_from_period_separated_keys(tc)

        with assume:
            assert str(exc.value) == 'Nested keys overlap.', tc


def test_create_nested_dict_from_period_separated_keys_fails_when_dict_vals():
    test_cases = [
        {
            'a': 1,
            'a.b': {'c': 'd'}
        },

    ]
    for tc in test_cases:
        with pytest.raises(ValueError) as exc:
            create_nested_dict_from_period_separated_keys(tc)

        with assume:
            assert str(exc.value) == "Values can't be dicts.", tc


def test_nested_dict_to_html():
    test_cases = [
        (
            {
                'a': 1
            },
            '\n<br> a: 1'
        ),
        (
            {
                'a': {
                    'b': 12
                }
            },
            ""
        )
    ]

    for d, expected in test_cases:
        html = nested_dict_to_html(d)
        with assume: assert html == expected, d
