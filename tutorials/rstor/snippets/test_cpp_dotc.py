import numpy as np
import et_dot

# create alias to dotc binary extension module:
cpp = et_dot.dotc

def test_dotc_aa():
    a = np.array([0, 1, 2, 3, 4], dtype=float)
    expected = np.dot(a, a)
    # call function dotc in the binary extension module:
    a_dot_a = cpp.dot(a, a)
    assert a_dot_a == expected
