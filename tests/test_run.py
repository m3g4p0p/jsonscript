# -*- coding: utf-8 -*-
import json

import pytest

from jsonscript.interpreter import run


class TestStandalonePrefixes:
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


class TestPrefixes:
    def test_return(self):
        assert run({
            'spam': {
                '+': ['&0', 1]
            },
            '#': {
                'spam': [41]
            }
        }) == run({
            'spam': {
                '+': ['&0', 1]
            },
            '#spam': [41]
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


class TestControlFlow:
    def test_if(self):
        assert run({'if': [True, 42]}) == 42
        assert run({'if': [False, 42]}) is None

    def test_if_else(self):
        assert run({'if': [True, 42, 'spam']}) == 42
        assert run({'if': [False, 42, 'eggs']}) == 'eggs'


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
                '@bind': ['spam'],
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
                '@bind': ['spam'],
                '=eggs': 41,
                '!&spam': [1],
                '#': '&eggs'
            }
        }) == 41

        assert capsys.readouterr().out == '42\n'


class TestIO:
    def test_read_file(self, tmp_path):
        f = tmp_path / 'spam.txt'
        f.write_text('eggs')

        assert run({
            'read': [str(f)]
        }) == 'eggs'

    def test_write_file(self, tmp_path):
        f = tmp_path / 'spam.txt'
        run({'write': [str(f), 'eggs']})

        assert f.read_text() == 'eggs'


class TestModules:

    @staticmethod
    @pytest.fixture
    def create_json(tmp_path):
        def create(file_path, obj):
            file = tmp_path / file_path
            file.parent.mkdir(exist_ok=True, parents=True)

            with open(file, 'w') as f:
                json.dump(obj, f)

            return file

        return create

    def test_run_file(self, create_json):
        main = create_json('spam.json', {'#': 42})
        assert run(main) == 42

    def test_imports(self, create_json):
        main = create_json('spam.json', {
            '@import': {
                'eggs': ['func', 'foo']
            },
            '=foo': {'*': ['&foo', 5]},
            'func': [{'+': ['&foo', 1]}]
        })

        create_json('eggs.json', {
            '@export': ['foo', 'bar', 'func'],
            '=foo': 4,
            '=bar': 2,
            'func': {
                '*': ['&0', '&bar']
            }
        })

        assert run(main) == 42

    def test_run_module_only_once(self, create_json, capsys):
        main = create_json('spam.json', {
            '@import': {
                'eggs': ['foo'],
                'ham': ['bar']
            },
            '!print': ['spam'],
            '+': ['&foo', '&bar']
        })

        create_json('eggs.json', {
            '@import': {
                'ham': ['bar']
            },
            '@export': ['foo'],
            '!print': ['eggs'],
            '=foo': {'+': [40, '&bar']},
        })

        create_json('ham.json', {
            '@export': ['bar'],
            '!print': ['ham'],
            '=bar': 1,
        })

        assert run(main) == 42
        assert capsys.readouterr().out == 'ham\neggs\nspam\n'

    def test_relative_import_paths(self, create_json):
        main = create_json('foo/spam.json', {
            '@import': {
                '../bar/eggs': ['value'],
            },
            '#': '&value'
        })

        create_json('bar/eggs.json', {
            '@import': {
                'baz/ham.json': ['value']
            },
            '@export': ['value']
        })

        create_json('bar/baz/ham.json', {
            '@export': ['value'],
            '=value': 42,
        })

        assert run(main) == 42

    def test_nested_imports(self, create_json):
        main = create_json('foo/spam.json', {
            '#': {
                '@import': {
                    '../bar/eggs': ['value'],
                },
                '#': '&value'
            }
        })

        create_json('bar/eggs.json', {
            '@export': ['value'],
            '=value': 42
        })

        assert run(main) == 42


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
