# whool

A standard-compliant Python build backend to package Odoo addons.

## Quick start

Create a file named `pyproject.toml` next to the addon's `__manifest__.py` with the
following content:

```toml
[build-system]
requires = ["whool"]
build-backend = "whool.buildapi"
```

Tip: you can use the `pipx run whool init` command to do that.

When that is done you can work with the addon as any regular python project. Notably

- `pipx run build --wheel --outdir /tmp/dist/` or
  `pip wheel --no-deps --wheel-dir /tmp/dist/ .` will create a wheel.
- Assuming `odoo` has been installed with pip in the current Python environment (for
  instance with `pip install --editable ./odoo`), `pip install --editable .` will
  install the addon and its dependencies (which it will pull from PyPI) and make it
  available in the Odoo addons path without the need to modify Odoo's `--addons-path`
  option.

## Interaction with git

`whool` will package all the files that are under `git` control and ignore everything
else.

The version of the generated distribution packages is also influenced by the `git`
commit history in the following way. TODO...

## Configuration

The following options can be set in `pyproject.toml`:

```toml
[tool.whool]
# TODO explain this (see setuptools-odoo docs in the meantime)
depends_override = {}
external_dependencies_override = {}
post_version_strategy_override = "..."
odoo_version_override = "..."
```

If set the following environment variables override the corresponding `pyproject.toml` options:

- `WHOOL_POST_VERSION_STRATEGY_OVERRIDE`

## Comparison to setuptools-odoo

This project is the successor of
[setuptools-odoo](https://pypi.org/project/setuptools-odoo/), as a standard-compliant
Python build backend.

The main expected benefit of `whool` over `setuptools-odoo` is that the `setup`
directory and `setup.py` files are replaced by a `pyproject.toml` file at the root of
each addon. It is less intrusive, and does not need symbolic links for regular
operation.

`setuptools-odoo` relied on little documented hooks and deprecated extension
mechanisms of `setuptools`, which was progressively causing compatibility issues.

`setuptools-odoo` provided a mechanism to package a multi-addon project. This
is now covered by the [hatch-odoo](https://pypi.org/project/hatch-odoo/) project.

## Development

To release and publish to PyPI, go to GitHub and create a release.
