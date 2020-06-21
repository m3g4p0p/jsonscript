# -*- coding: utf-8 -*-

from jsonscript.runner import run


def test_return():
    assert run({'#': 42}) == 42


def test_variable():
    assert run({
        '$spam': 42,
        '#': '$spam'
    }) == 42


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


def _test_recursion():
    assert run({
        'fac': {
            'if': [{'is': ['$0', 1]}, 1, {
                '*': ['$0', {'fac': [{'-': ['$0', 1]}]}]
            }]
        },
        '#': {'fac': [5]}

    }) == 120
