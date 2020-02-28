#!/usr/bin/env python

import os
import click
from executor import execute


def python_source_files():
    import glob

    include_paths = (
        glob.glob("*.py")
        + glob.glob("hobart/*.py")
        + glob.glob("hobart/**/*.py")
        + ["doc/"]
    )
    exclude_paths = []
    return [x for x in include_paths if x not in exclude_paths]


@click.group()
def cli():
    pass


@cli.command()
def init():
    execute("pip3 install --upgrade -r requirements_dev.txt")


@cli.command()
def test():
    execute("pytest")


@cli.command()
def coverage():
    execute("pytest --cov=hobart")


@cli.command()
def coverage_report():
    execute("coverage html")
    execute("open htmlcov/index.html")


@cli.command()
def lint():
    execute("flake8", *python_source_files())


@cli.command()
def black():
    execute("black", *python_source_files())


@cli.command()
def black_check():
    execute("black", "--check", *python_source_files())


@cli.command()
def doc():
    execute("rm -rf build/ doc/build/ doc/api/")
    execute("sphinx-build -W -b singlehtml doc doc/build")


@cli.command()
def doc_open():
    execute("open doc/build/index.html")


@cli.command()
def clean():
    execute("find . -name '*.pyc' -delete")
    execute("find . -name '__pycache__' -delete")


@cli.command()
def publish():
    execute("rm -rf dist/ build/")
    execute("python3 setup.py sdist bdist_wheel")
    execute("twine upload dist/*")


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    cli()
