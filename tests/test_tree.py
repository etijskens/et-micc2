from pathlib import Path

from et_micc2.tools.env import list_folders_only

def test_tree():
    contents = list_folders_only(Path())
    for entry in contents:
        print(entry)
    assert 'subcmds' in contents
    assert 'tools' in contents
    assert 'templates' in contents


if __name__ == "__main__":
    the_test_you_want_to_debug = test_tree

    print(f"{__file__}::__main__ executing test '{the_test_you_want_to_debug}'")
    the_test_you_want_to_debug()

    print('-*# finished #*-')
