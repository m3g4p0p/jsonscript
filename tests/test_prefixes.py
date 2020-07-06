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


class TestActualPrefixes:
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
