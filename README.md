# whool - Package Odoo Addons as Python Wheels

!!! pre-alpha work in progress...

This project is the successor of setuptools-odoo, as a PEP 517 build backend.

It also provides a convenience CLI to build and install addons, although
this can also be achieved with regular Python packaging ecosystem tools
such as `pip` and `build`.

Main expected benefit: the setup directory is replaced by
a `pyproject.toml` file at the root of each addon. So it's less intrusive,
and does not need symbolic links so it works better on platforms where
symlinks are problematic.

It currently depends on `setuptools-odoo` where the logic to extract
Python Package Metadata from Odoo Addon Manifests resides.
