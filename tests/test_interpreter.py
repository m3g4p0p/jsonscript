# -*- coding: utf-8 -*-
from jsonscript.interpreter import run


class TestPipe:
    def test_pipe_functions(self):
        assert run({
            'foo': {'+': ['&0', 1]},
            'bar': {'*': ['&0', 2]},
            'baz': {'/': ['&0', '&1']},
            'baz|foo|bar': [60, 3]
        }) == 42

    def test_pipe_bound_function(self):
        assert run({
            '=spam': 2,
            'foo': {'+': ['&0', '&spam']},
            'bar': {'*': ['&0', '&spam']},
            'baz': {'/': ['&0', '&eggs']},
            '#': {
                '=spam': 1,
                '=eggs': 3,
                '&baz|&foo|bar': [60]
            }
        }) == 42


class TestAssignment:
    def test_primitive(self):
        assert run({
            '=spam': 42,
            '#': '&spam'
        }) == 42

    def test_evaluate_list(self):
        assert run({
            '=spam': 42,
            '=eggs': ['foo', '&spam', {'#': 'bar'}],
            '#': '&eggs'
        }) == ['foo', 42, 'bar']

    def test_evaluate_dict(self):
        assert run({
            '=spam': {'#': 42},
            '#': '&spam'
        }) == 42


class TestReferences:
    def test_callback_reference(self):
        assert run({
            'spam': {
                '@params': ['callback', 'value'],
                'callback': ['&value']
            },
            '#': {
                'eggs': {
                    '+': ['&0', 1]
                },
                'spam': ['&eggs', 41]
            }
        })


class TestParameters:
    def test_params(self):
        assert run({
            'spam': {
                '@params': ['foo', 'bar'],
                '+': ['&foo', '&bar']
            },
            '#spam': [40, 2]
        }) == 42

    def test_args(self):
        assert run({
            'spam': {
                '#': '&args'
            },
            '#spam': [1, 2, 3]
        }) == (1, 2, 3)

        assert run({
            'spam': {
                '#': {
                    '#': '&args'
                }
            },
            '#spam': [1, 2, 3]
        }) == (1, 2, 3)

    def test_this(self):
        assert run({
            'factory': {
                '=value': 42,
                '#': '&this'
            },
            '=spam': {'factory': []},
            'get': ['&spam', 'value']
        }) == 42

        assert run({
            'factory': {
                '=value': '&0',
                '#': '&this'
            },
            '=spam': {'factory': ['foo']},
            '=eggs': {'factory': ['bar']},
            '#': [
                {'get': ['&spam', 'value']},
                {'get': ['&eggs', 'value']},
            ]
        }) == ['foo', 'bar']


class TestUse:
    def test_use_scoped(self):
        assert run({
            '=spam': {
                '=foo': 41,
                '#': '&this'
            },
            'eggs': {
                '@use': ['spam'],
                '+': ['&foo', '&0']
            },
            '#eggs': [1]
        }) == 42

    def test_override_values(self):
        assert run({
            '=spam': {
                '=foo': 41,
                '=bar': 7,
                '#': '&this'
            },
            'eggs': {
                '@use': ['spam'],
                '=bar': 1,
                '+': ['&foo', '&bar']
            },
            '#eggs': []
        }) == 42

    def test_referential_identity(self):
        assert run({
            '=spam': {
                '=foo': [1],
                '#': '&this'
            },
            '!': {
                '@use': ['spam'],
                'push': ['&foo', 2]
            },
            'get': ['&spam', 'foo']
        }) == [1, 2]


class TestContextBinding:
    def test_preserve_scope(self):
        assert run({
            '=eggs': 1,
            'spam': {
                '+': ['&0', '&eggs']
            },
            '#': {
                '=eggs': 41,
                'spam': ['&eggs']
            }
        }) == 42

    def test_bind_scope(self):
        assert run({
            '=eggs': 1,
            'spam': {
                '+': ['&0', '&eggs']
            },
            '#': {
                '=eggs': 41,
                '&spam': [1]
            }
        }) == 42

    def test_bound_reference(self):
        assert run({
            '=eggs': 1,
            'spam': {'+': ['&0', '&eggs']},
            'ham': {
                '@params': ['callback'],
                '&callback': [1]
            },
            '#': {
                '=eggs': 41,
                '&ham': ['&spam']
            }
        }) == 42

    def test_bind_prefixed(self, capsys):
        assert run({
            '=eggs': 1,
            'spam': {
                'print': [{'+': ['&0', '&eggs']}]
            },
            '#': {
                '=eggs': 41,
                '!&spam': [1],
                '#': '&eggs'
            }
        }) == 41

        assert capsys.readouterr().out == '42\n'


class TestRandomAlgorithms:
    def test_factorial(self):
        assert run({
            'fac': {
                '?if': [{'==': ['&0', 1]}, 1],
                '*': ['&0', {'fac': [{'-': ['&0', 1]}]}]
            },
            '#': {'fac': [5]}
        }) == 120

    def test_fibonacci(self):
        assert run({
            'fibo': {
                '?if': [{'or': [
                    {'==': ['&0', 1]},
                    {'==': ['&0', 2]}
                ]}, 1],
                '+': [
                    {'fibo': [{'-': ['&0', 1]}]},
                    {'fibo': [{'-': ['&0', 2]}]}
                ]
            },
            '#': {
                'fibo': [7]
            }
        }) == 13

    def test_map(self):
        assert run({
            'map': {
                '@params': ['list', 'callback'],
                '?if': [{'==': [{'length': ['&list']}, 0]}, []],
                '=list': {'copy': ['&list']},
                '=current': {'callback': [{'pop': ['&list']}]},
                '=result': {'map': ['&list', '&callback']},
                '!push': ['&result', '&current'],
                '#': '&result'
            },
            '#': {
                'inc': {'+': ['&0', 1]},
                'map': [[1, 2, 3], '&inc']
            }
        }) == [2, 3, 4]
