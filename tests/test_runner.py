# -*- coding: utf-8 -*-

from jsonscript.runner import run


def test_return():
    assert run({'#': 42}) == 42


def test_variable():
    assert run({
        '$spam': 42,
        '#': '$spam'
    }) == 42


def test_list():
    assert run({
        '$spam': 42,
        '$eggs': ['foo', '$spam', {'#': 'bar'}],
        '#': '$eggs'
    }) == ['foo', 42, 'bar']


def test_function():
    assert run({
        'spam': {
            '+': ['$0', 1]
        },
        '#': {
            'spam': [41]
        }
    }) == 42


def test_preserve_scope():
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


def test_side_effect(capsys):
    assert run({
        '&print': ['spam'],
        '#': 42
    }) == 42

    assert capsys.readouterr().out == 'spam\n'


def test_named_params():
    assert run({
        'spam': {
            '@params': ['foo', 'bar'],
            '+': ['$foo', '$bar']
        },
        '#': {
            'spam': [40, 2]
        }
    }) == 42


def _test_recursion():
    assert run({
        'fac': {
            'if': [{'is': ['$0', 1]}, 1, {
                '*': ['$0', {'fac': [{'-': ['$0', 1]}]}]
            }]
        },
        '#': {'fac': [5]}

    }) == 120
