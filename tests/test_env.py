from pathlib import Path

from et_micc2.tools.env import common_path
from et_micc2.tools.utils import in_directory

def test_common_path_1():
    """"""
    paths = [
        'et_micc2/scripts',
        'et_micc2/subcmds/check_env.py',
        'et_micc2/templates/top-level-package/{{tmpl.project_name}}/.gitignore'
    ]
    result = common_path(paths)
    print(f"{result=}")
    expected = Path('et_micc2/')
    assert result == expected

def test_common_path_2():
    """"""
    with in_directory('/Users/etijskens/software/dev/workspace/et-micc2'):
        paths = [
            'et_micc2/scripts',
            'et_micc2/subcmds/check_env.py',
            'et_micc2/templates/top-level-package/{{tmpl.project_name}}/.gitignore'
        ]
        result = common_path(paths)
        print(f"{result=}")
        expected = Path('et_micc2/').resolve()
        assert result == expected

if __name__ == "__main__":
    the_test_you_want_to_debug = test_common_path_1

    print(f"{__file__}::__main__ executing test '{the_test_you_want_to_debug}'")
    the_test_you_want_to_debug()

    print('-*# finished #*-')
