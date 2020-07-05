from jsonscript.interpreter import run


class TestControlFlow:
    def test_if(self):
        assert run({'if': [True, 42]}) == 42
        assert run({'if': [False, 42]}) is None

    def test_if_else(self):
        assert run({'if': [True, 42, 'spam']}) == 42
        assert run({'if': [False, 42, 'eggs']}) == 'eggs'


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
