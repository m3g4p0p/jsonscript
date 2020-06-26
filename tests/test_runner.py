# -*- coding: utf-8 -*-

from jsonscript.runner import run


class TestStatements:
    def test_return(self):
        assert run({'#': 42}) == 42

    def test_maybe(self):
        assert run({'?': 42, '#': 'spam'}) == 42
        assert run({'?': None, '#': 'spam'}) == 'spam'

    def test_void(self):
        assert run({'!': 42}) is None

    def test_void_call(self, capsys):
        assert run({
            '!': {'print': ['spam']},
            '#': 42
        }) == 42

        assert capsys.readouterr().out == 'spam\n'


class TestControlFlow:
    def test_if(self):
        assert run({'?:': [True, 42]}) == 42
        assert run({'?:': [False, 42]}) is None

    def test_if_else(self):
        assert run({'?:': [True, 42, 'spam']}) == 42
        assert run({'?:': [False, 42, 'eggs']}) == 'eggs'


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


class TestLists:
    def test_push(self):
        assert run({
            '=spam': [42],
            '!push': ['&spam', 'eggs'],
            '#': '&spam'
        }) == [42, 'eggs']

    def test_pop(self):
        assert run({
            '=spam': [42, 'eggs'],
            '=eggs': {'pop': ['&spam']},
            '#': ['&spam', '&eggs']
        }) == [[42], 'eggs']


class TestFunctions:
    def test_return(self):
        assert run({
            'spam': {
                '+': ['&0', 1]
            },
            '#': {
                'spam': [41]
            }
        }) == 42

    def test_void(self, capsys):
        assert run({
            '!print': ['spam'],
            '#': 42
        }) == 42

        assert capsys.readouterr().out == 'spam\n'

    def test_maybe(self):
        assert run({
            '??:': [False, 'spam'],
            '#': {
                '??:': [True, 42]
            }
        }) == 42


class TestDirectives:
    def test_params(self):
        assert run({
            'spam': {
                '@params': ['foo', 'bar'],
                '+': ['&foo', '&bar']
            },
            '#': {
                'spam': [40, 2]
            }
        }) == 42


class TestReferences:
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

    def test_scope_reference(self):
        assert run({
            '&spam': {
                '+': ['&0', '&eggs']
            },
            '#': {
                '=eggs': 41,
                'spam': [1]
            }
        }) == 42

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

    def test_combined(self):
        assert run({
            '&spam': {'+': ['&0', '&eggs']},
            '&ham': {
                '@params': ['callback'],
                'callback': [1]
            },
            '#': {
                '=eggs': 41,
                'ham': ['&spam']
            }
        }) == 42


class TestAlgorithms:
    def test_factorial(self):
        assert run({
            'fac': {
                '??:': [{'==': ['&0', 1]}, 1],
                '*': ['&0', {'fac': [{'-': ['&0', 1]}]}]
            },
            '#': {'fac': [5]}
        }) == 120

    def test_fibonacci(self):
        assert run({
            'fibo': {
                '??:': [{'or': [
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
                '??:': [{'==': [{'length': ['&list']}, 0]}, []],
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
