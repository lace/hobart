import numpy as np


def check_indices(indices, num_elements, name):
    # Vendored in from lacecore.
    if np.any(indices >= num_elements):
        raise ValueError(
            "Expected indices in {} to be less than {}".format(name, num_elements)
        )
