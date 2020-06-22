# -*- coding: utf-8 -*-

from jsonscript.runner import run


class TestStatements:
    def test_return(self):
        assert run({'#': 42}) == 42

    def test_maybe(self):
        assert run({'?': 42, '#': 'spam'}) == 42
        assert run({'?': None, '#': 'spam'}) == 'spam'


class TestVariables:
    def test_primitive(self):
        assert run({
            '$spam': 42,
            '#': '$spam'
        }) == 42

    def test_list(self):
        assert run({
            '$spam': 42,
            '$eggs': ['foo', '$spam', {'#': 'bar'}],
            '#': '$eggs'
        }) == ['foo', 42, 'bar']


class TestFunctions:
    def test_return(self):
        assert run({
            'spam': {
                '+': ['$0', 1]
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
            '?if': [False, 'spam'],
            '#': {
                '?if': [True, 42]
            }
        }) == 42

    def test_preserve_scope(self):
        assert run({
            '$eggs': 1,
            'spam': {
                '+': ['$0', '$eggs']
            },
            '#': {
                '$eggs': 41,
                'spam': ['$eggs']
            }
        }) == 42


class TestDirectives:
    def test_params(self):
        assert run({
            'spam': {
                '@params': ['$foo', '$bar'],
                '+': ['$foo', '$bar']
            },
            '#': {
                'spam': [40, 2]
            }
        }) == 42


class TestReferences:
    def test_scope_reference(self):
        assert run({
            '&spam': {
                '+': ['$0', '$eggs']
            },
            '#': {
                '$eggs': 41,
                'spam': [1]
            }
        }) == 42

    def test_callback_reference(self):
        assert run({
            'spam': {
                '@params': ['callback', '$value'],
                'callback': ['$value']
            },
            '#': {
                'eggs': {
                    '+': ['$0', 1]
                },
                'spam': ['&eggs', 41]
            }
        })

    def test_combined(self):
        assert run({
            '&spam': {'+': ['$0', '$eggs']},
            '&ham': {
                '@params': ['callback'],
                'callback': [1]
            },
            '#': {
                '$eggs': 41,
                'ham': ['&spam']
            }
        }) == 42


class TestAlgorithms:
    def test_factorial(self):
        assert run({
            'fac': {
                '?if': [{'is': ['$0', 1]}, 1],
                '*': ['$0', {'fac': [{'-': ['$0', 1]}]}]
            },
            '#': {'fac': [5]}
        }) == 120

    def test_fibonacci(self):
        assert run({
            'fibo': {
                '?if': [{'or': [
                    {'is': ['$0', 1]},
                    {'is': ['$0', 2]}
                ]}, 1],
                '+': [
                    {'fibo': [{'-': ['$0', 1]}]},
                    {'fibo': [{'-': ['$0', 2]}]}
                ]
            },
            '#': {
                'fibo': [7]
            }
        }) == 13
