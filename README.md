# hobart

[![version](https://img.shields.io/pypi/v/hobart?style=flat-square)][pypi]
[![python versions](https://img.shields.io/pypi/pyversions/hobart?style=flat-square)][pypi]
[![license](https://img.shields.io/pypi/l/hobart?style=flat-square)][pypi]
[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=flat-square)][coverage]
[![build](https://img.shields.io/circleci/project/github/lace/hobart/master?style=flat-square)][build]
[![code style](https://img.shields.io/badge/code%20style-black-black?style=flat-square)][black]

Obtain cross sections of polygonal meshes.

This library is optimized for cloud computation, however it depends on both
[NumPy][] and [the SciPy k-d tree][ckdtree]. It's designed for use with
[lacecore][].

Currently works only with triangular meshes.

Prior to version 1.0, this was a library for rendering mesh cross sections to
SVG. That library has been renamed to [hobart-svg][].

[pypi]: https://pypi.org/project/hobart/
[coverage]: https://github.com/lace/hobart/blob/master/.coveragerc#L2
[build]: https://circleci.com/gh/lace/hobart/tree/master
[docs build]: https://hobart.readthedocs.io/en/latest/
[black]: https://black.readthedocs.io/en/stable/
[trimesh]: https://trimsh.org/
[numpy]: https://numpy.org/
[ckdtree]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.html
[lacecore]: https://github.com/lace/lacecore
[hobart-svg]: https://github.com/lace/hobart-svg

## Contribute

- Issue Tracker: https://github.com/lace/hobart/issues
- Source Code: https://github.com/lace/hobart

Pull requests welcome!


## Support

If you are having issues, please let us know.


## Acknowledgements

This library was based on code in [Lace][], which was refactored from legacy
code at Body Labs by [Alex Weiss][], with portions by [Eric Rachlin][],
[Paul Melnikow][], [Victor Alvarez][], and others. Later it was extracted
from the Body Labs codebase and open-sourced by [Guillaume Marceau][]. In
2018 it was [forked by Paul Melnikow][fork] and published as
[metabolace][fork pypi]. Thanks to a repository and package transfer from
Body Labs, the fork has been merged back into the original.

[lace]: http://github.com/lace/lace
[paul melnikow]: https://github.com/paulmelnikow
[jake beard]: https://github.com/jbeard4
[alex weiss]: https://github.com/algrs
[eric rachlin]: https://github.com/eerac
[victor alvarez]: https://github.com/yangmillstheory
[guillaume marceau]: https://github.com/gmarceau
[fork]: https://github.com/metabolize/lace
[fork pypi]: https://pypi.org/project/metabolace/

## License

The project is licensed under the two-clause BSD license.
