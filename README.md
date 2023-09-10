# whool - Package Odoo Addons as Python Wheels

This project is the successor of
[setuptools-odoo](https://pypi.org/project/setuptools-odoo/), as a standard-compliant
Python build backend.

It also provides a CLI to initialize `pyproject.toml` in an addon directory.

The main expected benefit is that the the setup directory is replaced by a
`pyproject.toml` file at the root of each addon. So it's less intrusive, and does not
need symbolic links for regular operation.

## Configuration

The following options can be set in `pyproject.toml`:

... TODO

## Development

To release and publish to PyPI, go to GitHub and create a release.
