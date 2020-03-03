# Vendored in from lacecore.

import numpy as np
import pytest
from ._validation import check_indices


def test_check_indices_valid():
    check_indices(np.repeat(np.arange(8), 3).reshape(-1, 3), 8, "f")
    check_indices(np.zeros((0, 3)), 8, "f")


def test_check_indices_invalid():
    with pytest.raises(ValueError, match="Expected indices in f to be less than 8"):
        check_indices(np.arange(24).reshape(-1, 3), 8, "f")
