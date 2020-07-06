import json

import pytest

from jsonscript.interpreter import run


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

    def test_import_all(self, create_json):
        imports_all = create_json('spam.json', {
            '@import': {
                'eggs': True
            },
            '+': ['&foo', '&bar']
        })

        imports_foo = create_json('ham.json', {
            '@import': {
                'eggs': ['foo']
            },
            '+': ['&foo', '&bar']
        })

        create_json('eggs.json', {
            '@export': ['foo', 'bar'],
            '=foo': 41,
            '=bar': 1,
        })

        assert run(imports_all) == 42

        with pytest.raises(KeyError):
            run(imports_foo)

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

    def test_sublevel_imports(self, create_json):
        main = create_json('spam.json', {
            '@import': {
                'eggs': ['foo'],
            },
            '#': {
                '@import': {
                    'eggs': ['bar'],
                },
                '+': ['&foo', '&bar']
            }
        })

        create_json('eggs.json', {
            '@export': ['foo', 'bar'],
            '=foo': 41,
            '=bar': 1
        })

        assert run(main) == 42

    def test_sublevel_exports(self, create_json):
        main = create_json('spam.json', {
            '@import': {
                'eggs': ['foo', 'bar'],
            },
            '+': ['&foo', '&bar']
        })

        create_json('eggs.json', {
            '@export': ['foo'],
            '=foo': 41,
            '#': {
                '@export': ['bar'],
                '=bar': 1
            }
        })

        assert run(main) == 42
