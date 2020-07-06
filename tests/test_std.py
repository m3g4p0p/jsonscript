from jsonscript.interpreter import run


class TestControlFlow:
    def test_if(self):
        assert run({'if': [True, 42]}) == 42
        assert run({'if': [False, 42]}) is None

    def test_if_else(self):
        assert run({'if': [True, 42, 'spam']}) == 42
        assert run({'if': [False, 42, 'eggs']}) == 'eggs'


class TestTypeConversion:
    def test_number(self):
        assert run({'number': ['42']}) == 42
        assert run({'number': ['4.2']}) == 4.2

    def test_string(self):
        assert run({'string': [42]}) == '42'

    def test_boolean(self):
        assert run({'boolean': [42]}) is True
        assert run({'boolean': ['42']}) is True
        assert run({'boolean': [0]}) is False
        assert run({'boolean': ['']}) is False


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

    def test_slice(self):
        assert run({
            'slice': [[1, 2, 3]]
        }) == [1, 2, 3]

        assert run({
            'slice': [[1, 2, 3], 1]
        }) == [2, 3]

        assert run({
            'slice': [[1, 2, 3], 0, -1]
        }) == [1, 2]

    def test_get(self):
        assert run({
            'get': [[1, 2, 3], 1]
        }) == 2

    def test_set(self):
        assert run({
            '=spam': [1, 2, 3],
            '!set': ['&spam', 1, 4],
            '#': '&spam'
        }) == [1, 4, 3]


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
