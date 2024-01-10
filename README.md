# whool

A standards-compliant Python build backend to package individual Odoo addons.

## Quick start

Create a file named `pyproject.toml` next to the addon's `__manifest__.py` with the
following content:

```toml
[build-system]
requires = ["whool"]
build-backend = "whool.buildapi"
```

> 💡 you can use the `pipx run whool init` command to do that.

When that is done you can work with the addon as any regular python project. Notably

- `pipx run build --wheel --outdir /tmp/dist/` or
  `pip wheel --no-deps --wheel-dir /tmp/dist/ .` will create a wheel.
- Assuming `odoo` has been installed with pip in the current Python environment (for
  instance with `pip install --editable ./odoo`), `pip install --editable .` will
  install the addon and its dependencies (which it will pull from PyPI) and make it
  available in the Odoo addons path without the need to modify Odoo's `--addons-path`
  option.

## Files included in the distribution packages

`whool` will package all the files that are under `git` control and ignore everything
else.

> 📝 TODO: explain what is included in a sdist vs wheel, and how building from a sdist works.

## Version number of the generated packages

The version of the generated distribution packages is influenced by the `git`
commit history in the following way.

> 📝 TODO: elaborate (see setuptools-odoo docs in the meantime)

## Configuration

The following options can be set in `pyproject.toml`:

> 📝 TODO: explain this (see setuptools-odoo docs in the meantime)

```toml
[tool.whool]
depends_override = {}
external_dependencies_override = {}
post_version_strategy_override = "..."
odoo_series_override = "..."
```

If set, the following environment variables override the corresponding `pyproject.toml`
options:

- `WHOOL_POST_VERSION_STRATEGY_OVERRIDE`


## Standard compliance

`whool` is compliant with [PEP 517](https://peps.python.org/pep-0517/) and [PEP
660](https://peps.python.org/pep-0660/), so it is compatible with all Python build
frontends, and supports editable installs.

> [!NOTE]
> Editable install require support for symbolic links, which are available on most
> platforms but may not be enabled by default on Windows.

It supports the optional `prepare_metadata_for_build_wheel` and
`prepare_metadata_for_build_editable` hooks, for faster metadata preparation.

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

The equivalent of the `setuptools-odoo-make-default` command is now `whool init`, which
can initialize a `pyproject.toml` in the current directory if it is an addon, or in all
immediate subrectories that are addons.

An equivalent of `setuptools-odoo-get-requirements` can now easily be built using
standard-based tools such as [pyproject-dependencies](https://pypi.org/project/pyproject-dependencies).
An example can be found in [OCA/maintainer-tools](https://github.com/OCA/maintainer-tools/blob/master/tools/gen_external_dependencies.py).

## Development

To release and publish to PyPI:

- Update the changelog by running `towncrier build --version X.Y.Z`.
- Commit and push the changes.
- Go to GitHub and create a release with a tag `vX.Y.Z`.

The release will be uploaded to PyPI automatically.
