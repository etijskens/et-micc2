from pathlib import Path

from et_micc2.tools.components import ComponentDatabase
import et_micc2.tools.utils as utils

from tests import helpers

def test_components():
    with utils.in_directory(helpers.test_workspace()):
        results = []
        # Create package BAR
        results.append(helpers.micc(['-p', 'BAR', 'create', '--allow-nesting', '--remote=none']))
        assert Path('BAR/bar/__init__.py').exists()
        # add Python submodule 'foo'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo', '--py']))
        assert Path('BAR/bar/foo/__init__.py').exists()
        assert Path('BAR/components.json').exists()
        # add Python submodule 'foo2'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo2', '--py']))
        assert Path('BAR/bar/foo2/__init__.py').exists()
        # add Python submodule 'foo/soup'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo/soup', '--py']))
        assert Path('BAR/bar/foo/soup/__init__.py').exists()
        # add Python submodule 'foo2/soup'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo2/soup2', '--py']))
        assert Path('BAR/bar/foo2/soup2/__init__.py').exists()

        components = ComponentDatabase(Path('BAR'))
        similar = components.similar_to('foo')
        print(f"{similar=}")
        assert 'foo' in similar
        assert 'foo2' in similar
        assert 'foo2/soup2' in similar

        key = components.has_name('foo')
        print(f"{key=}")
        assert key == 'foo'

if __name__ == "__main__":
    the_test_you_want_to_debug = test_components

    print(f"{__file__}::__main__ executing test '{the_test_you_want_to_debug}'")
    the_test_you_want_to_debug()

    print('-*# finished #*-')
