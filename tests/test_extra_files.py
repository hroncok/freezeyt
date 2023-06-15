import pytest
from pathlib import Path

from freezeyt.extra_files import get_extra_files
from freezeyt import freeze

from testutil import FIXTURES_PATH, context_for_test

IMAGE_BYTES = b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR\0\0\0\x08\0\0\0\x08\x08\x04\0\0\0n\x06v\0\0\0\0#IDAT\x08\xd7cd``\xf8\xcf\x80\0\x8c\xa8\\ \x8f\tB!\x91D\xab\xf8\x8f\x10D\xd3\xc2\x88n-\0\x0e\x1b\x0f\xf9LT9_\0\0\0\0IEND\xaeB`\x82'

def test_simple():
    config = {
        'extra_files': {
            'foo': 'abc',
        }
    }
    assert list(get_extra_files(config)) == [('foo', 'content', b'abc')]


EXTRA_FILES = {
    'url_part': {'url_part': b'a'},
    '/url_part': {'url_part': b'a'},
    'url_part/': {'url_part': {'index.html': b'a'}},
    '/url_part/': {'url_part': {'index.html': b'a'}},
    '/url_part//': {'url_part': {'index.html': b'a'}},
    '//url_part/': {'url_part': {'index.html': b'a'}},
    '/path_to//file': {'path_to': {'file': b'a'}},
    'path_to///file': {'path_to': {'file': b'a'}},
    '/part1///part2/': {'part1': {'part2': {'index.html': b'a'}}},
    '/http/https/': {'http': {'https': {'index.html': b'a'}}},
    '/http\\https/': {'http': {'https': {'index.html': b'a'}}},
}
@pytest.mark.parametrize('test_case', EXTRA_FILES)
def test_slashes(test_case):
    extra_file = {test_case: 'a'}
    expected = EXTRA_FILES[test_case]
    config = {
        'extra_files': extra_file,
        'output': {'type': 'dict'},
    }

    with context_for_test('app_simple') as module:
        result = freeze(module.app, config)

    # pop to simplify syntax of expected dict
    # index.html is root page for app_simple, not useful for this test
    result.pop('index.html')

    assert result == expected


def test_content():
    config = {
        'extra_files': {
            'str.txt': 'ábč',
            'bytes.dat': b'def',
            'base64.dat': {'base64': 'Z2hp'},
            'copied.png': {
                'copy_from': FIXTURES_PATH / 'app_with_extra_files/smile2.png'
            },
            'directory': {
                'copy_from': 'some/dir',
            },
        }
    }
    assert sorted(get_extra_files(config)) == sorted([
        ('str.txt', 'content', 'ábč'.encode()),
        ('bytes.dat', 'content', b'def'),
        ('base64.dat', 'content', b'ghi'),
        ('copied.png', 'path', FIXTURES_PATH / 'app_with_extra_files/smile2.png'),
        ('directory', 'path', Path('some/dir')),
    ])
